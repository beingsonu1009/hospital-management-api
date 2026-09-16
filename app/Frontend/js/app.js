/* =========================================================
   HOSPITAL MANAGEMENT FRONTEND
   Main JavaScript
   ========================================================= */

/* =========================================================
   API CONFIGURATION
   ========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";


/* =========================================================
   GLOBAL STATE
   ========================================================= */

let accessToken = localStorage.getItem("access_token") || "";

let currentUser = localStorage.getItem("username") || "";

let editingPatientId = null;
let editingDoctorId = null;
let editingWorkingHoursId = null;

let appointmentPatients = [];
let appointmentDoctors = [];


/* =========================================================
   DOM REFERENCES
   ========================================================= */

// Authentication
const loginPage = document.getElementById("loginPage");
const loginForm = document.getElementById("loginForm");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const loginMessage = document.getElementById("loginMessage");

// Application
const appPage = document.getElementById("appPage");
const logoutButton = document.getElementById("logoutButton");
const pageTitle = document.getElementById("pageTitle");
const loggedInUser = document.getElementById("loggedInUser");

// Navigation
const navButtons = document.querySelectorAll("[data-section]");
const pageSections = document.querySelectorAll(".page-section");

// Dashboard
const patientCount = document.getElementById("patientCount");
const doctorCount = document.getElementById("doctorCount");
const appointmentCount = document.getElementById("appointmentCount");
const refreshDashboard = document.getElementById("refreshDashboard");
const dashboardStatus = document.getElementById("dashboardStatus");

// Patients
const showPatientFormBtn = document.getElementById("showPatientFormBtn");
const patientFormCard = document.getElementById("patientFormCard");
const patientForm = document.getElementById("patientForm");
const patientFormTitle = document.getElementById("patientFormTitle");
const editingPatientIdInput = document.getElementById("editingPatientId");

const patientName = document.getElementById("patientName");
const patientAge = document.getElementById("patientAge");
const patientGender = document.getElementById("patientGender");
const patientPhone = document.getElementById("patientPhone");
const patientDisease = document.getElementById("patientDisease");

const cancelPatientBtn = document.getElementById("cancelPatientBtn");
const patientFormMessage = document.getElementById("patientFormMessage");
const refreshPatients = document.getElementById("refreshPatients");
const patientsTableBody = document.getElementById("patientsTableBody");

// Doctors
const showDoctorFormBtn = document.getElementById("showDoctorFormBtn");
const doctorFormCard = document.getElementById("doctorFormCard");
const doctorForm = document.getElementById("doctorForm");
const doctorFormTitle = document.getElementById("doctorFormTitle");
const editingDoctorIdInput = document.getElementById("editingDoctorId");

const doctorName = document.getElementById("doctorName");
const doctorSpecialisation = document.getElementById("doctorSpecialisation");
const doctorPhone = document.getElementById("doctorPhone");

const cancelDoctorBtn = document.getElementById("cancelDoctorBtn");
const doctorFormMessage = document.getElementById("doctorFormMessage");
const refreshDoctors = document.getElementById("refreshDoctors");
const doctorsTableBody = document.getElementById("doctorsTableBody");

// Working Hours
const workingHoursForm = document.getElementById("workingHoursForm");
const workingDoctor = document.getElementById("workingDoctor");
const workingDay = document.getElementById("workingDay");
const workingStartTime = document.getElementById("workingStartTime");
const workingEndTime = document.getElementById("workingEndTime");

const cancelWorkingEditBtn = document.getElementById("cancelWorkingEditBtn");
const workingHoursMessage = document.getElementById("workingHoursMessage");
const workingHoursTableBody = document.getElementById("workingHoursTableBody");

// Appointments
const appointmentForm = document.getElementById("appointmentForm");
const appointmentPatient = document.getElementById("appointmentPatient");
const appointmentDoctor = document.getElementById("appointmentDoctor");
const appointmentDate = document.getElementById("appointmentDate");
const appointmentStartTime = document.getElementById("appointmentStartTime");
const appointmentDuration = document.getElementById("appointmentDuration");
const appointmentReason = document.getElementById("appointmentReason");

const appointmentFormMessage = document.getElementById("appointmentFormMessage");
const refreshAppointments = document.getElementById("refreshAppointments");
const appointmentsTableBody = document.getElementById("appointmentsTableBody");

// Reschedule modal
const rescheduleModal = document.getElementById("rescheduleModal");
const rescheduleForm = document.getElementById("rescheduleForm");
const rescheduleAppointmentId = document.getElementById("rescheduleAppointmentId");
const rescheduleDate = document.getElementById("rescheduleDate");
const rescheduleStartTime = document.getElementById("rescheduleStartTime");
const rescheduleDuration = document.getElementById("rescheduleDuration");
const closeRescheduleModal = document.getElementById("closeRescheduleModal");
const rescheduleMessage = document.getElementById("rescheduleMessage");


/* =========================================================
   HELPER FUNCTIONS
   ========================================================= */

function showMessage(element, message, type = "info") {
    if (!element) return;

    element.textContent = message;
    element.className = `form-message show ${type}`;
}


function clearMessage(element) {
    if (!element) return;

    element.textContent = "";
    element.className = "form-message";
}


function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function formatDate(dateValue) {
    if (!dateValue) return "-";

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return dateValue;
    }

    return date.toLocaleDateString("en-IN");
}


function formatTime(timeValue) {
    if (!timeValue) return "-";

    return String(timeValue).substring(0, 5);
}


function getDayName(dayNumber) {
    const days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    };

    return days[dayNumber] || "-";
}


function getStatusClass(status) {
    if (!status) return "";

    const normalized = String(status).toLowerCase();

    if (normalized === "active") {
        return "status-active";
    }

    if (normalized === "cancelled" || normalized === "canceled") {
        return "status-cancelled";
    }

    if (normalized === "completed") {
        return "status-completed";
    }

    if (normalized === "pending") {
        return "status-pending";
    }

    return "";
}


function getErrorMessage(error) {
    if (!error) {
        return "Something went wrong";
    }

    if (typeof error === "string") {
        return error;
    }

    return error.message || "Something went wrong";
}


/* =========================================================
   API REQUEST
   ========================================================= */

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers = {
        ...(options.headers || {})
    };

    if (!(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 204) {
        return null;
    }

    let data = null;

    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        if (response.status === 401) {
            logout();
        }

        let message = "Request failed";

        if (data) {
            if (typeof data.detail === "string") {
                message = data.detail;
            } else if (Array.isArray(data.detail)) {
                message = data.detail
                    .map(item => item.msg || "Validation error")
                    .join(", ");
            } else if (data.message) {
                message = data.message;
            }
        }

        throw new Error(message);
    }

    return data;
}


/* =========================================================
   AUTHENTICATION
   ========================================================= */

async function login(username, password) {
    clearMessage(loginMessage);

    try {
        const data = await apiRequest("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                username,
                password
            })
        });

        accessToken = data.access_token;

        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("username", username);

        currentUser = username;

        showApplication();

    } catch (error) {
        showMessage(
            loginMessage,
            getErrorMessage(error),
            "error"
        );
    }
}


function logout() {
    accessToken = "";
    currentUser = "";

    localStorage.removeItem("access_token");
    localStorage.removeItem("username");

    if (appPage) {
        appPage.classList.add("hidden");
    }

    if (loginPage) {
        loginPage.classList.remove("hidden");
    }

    if (loginForm) {
        loginForm.reset();
    }

    clearMessage(loginMessage);
}


function showApplication() {
    if (loginPage) {
        loginPage.classList.add("hidden");
    }

    if (appPage) {
        appPage.classList.remove("hidden");
    }

    if (loggedInUser) {
        loggedInUser.textContent = currentUser
            ? `Logged in as: ${currentUser}`
            : "";
    }

    showSection("dashboard");
}


/* =========================================================
   LOGIN EVENT
   ========================================================= */

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const username = usernameInput?.value.trim();
        const password = passwordInput?.value || "";

        if (!username || !password) {
            showMessage(
                loginMessage,
                "Username and password are required",
                "error"
            );
            return;
        }

        await login(username, password);
    });
}


if (logoutButton) {
    logoutButton.addEventListener("click", logout);
}


/* =========================================================
   NAVIGATION
   ========================================================= */

async function showSection(sectionName) {
    pageSections.forEach(section => {
        section.classList.remove("active-section");
    });

    navButtons.forEach(button => {
        button.classList.remove("active");
    });

    const targetSection = document.getElementById(
        `${sectionName}Section`
    );

    if (targetSection) {
        targetSection.classList.add("active-section");
    }

    const activeButton = document.querySelector(
        `[data-section="${sectionName}"]`
    );

    if (activeButton) {
        activeButton.classList.add("active");
    }

    const titles = {
        dashboard: "Dashboard",
        patients: "Patients",
        doctors: "Doctors",
        appointments: "Appointments"
    };

    if (pageTitle) {
        pageTitle.textContent = titles[sectionName] || "Hospital Management";
    }

    if (sectionName === "dashboard") {
        await loadDashboard();
    }

    if (sectionName === "patients") {
        await loadPatients();
    }

    if (sectionName === "doctors") {
        await loadDoctors();
        await loadWorkingHoursDoctors();
    }

    if (sectionName === "appointments") {
        await Promise.all([
            loadAppointmentPatients(),
            loadAppointmentDoctors()
        ]);

        await loadAppointments();
    }
}


navButtons.forEach(button => {
    button.addEventListener("click", async () => {
        const section = button.dataset.section;

        if (section) {
            await showSection(section);
        }
    });
});


/* =========================================================
   DASHBOARD
   ========================================================= */

async function loadDashboard() {
    clearMessage(dashboardStatus);

    try {
        const [
            patients,
            doctors,
            appointments
        ] = await Promise.all([
            apiRequest("/patients"),
            apiRequest("/doctors"),
            apiRequest("/appointments/")
        ]);

        if (patientCount) {
            patientCount.textContent = Array.isArray(patients)
                ? patients.length
                : 0;
        }

        if (doctorCount) {
            doctorCount.textContent = Array.isArray(doctors)
                ? doctors.length
                : 0;
        }

        if (appointmentCount) {
            appointmentCount.textContent = Array.isArray(appointments)
                ? appointments.length
                : 0;
        }

    } catch (error) {
        showMessage(
            dashboardStatus,
            getErrorMessage(error),
            "error"
        );
    }
}


if (refreshDashboard) {
    refreshDashboard.addEventListener(
        "click",
        loadDashboard
    );
}


/* =========================================================
   PATIENT FORM
   ========================================================= */

function resetPatientForm() {
    editingPatientId = null;

    if (editingPatientIdInput) {
        editingPatientIdInput.value = "";
    }

    if (patientFormTitle) {
        patientFormTitle.textContent = "Add Patient";
    }

    if (patientForm) {
        patientForm.reset();
    }

    clearMessage(patientFormMessage);

    if (patientFormCard) {
        patientFormCard.classList.add("hidden");
    }
}


function openPatientForm(patient = null) {
    clearMessage(patientFormMessage);

    if (patientFormCard) {
        patientFormCard.classList.remove("hidden");
    }

    if (!patient) {
        editingPatientId = null;

        if (patientFormTitle) {
            patientFormTitle.textContent = "Add Patient";
        }

        if (patientForm) {
            patientForm.reset();
        }

        return;
    }

    editingPatientId = patient.id;

    if (editingPatientIdInput) {
        editingPatientIdInput.value = patient.id;
    }

    if (patientFormTitle) {
        patientFormTitle.textContent = "Edit Patient";
    }

    if (patientName) {
        patientName.value = patient.name || "";
    }

    if (patientAge) {
        patientAge.value = patient.age ?? "";
    }

    if (patientGender) {
        patientGender.value = patient.gender || "";
    }

    if (patientPhone) {
        patientPhone.value = patient.phone || "";
    }

    if (patientDisease) {
        patientDisease.value = patient.disease || "";
    }
}


if (showPatientFormBtn) {
    showPatientFormBtn.addEventListener("click", () => {
        openPatientForm();
    });
}


if (cancelPatientBtn) {
    cancelPatientBtn.addEventListener(
        "click",
        resetPatientForm
    );
}


/* =========================================================
   PATIENT CRUD
   ========================================================= */

async function loadPatients() {
    if (!patientsTableBody) return;

    patientsTableBody.innerHTML = `
        <tr>
            <td colspan="7" class="loading">
                Loading patients...
            </td>
        </tr>
    `;

    try {
        const patients = await apiRequest("/patients");

        if (!Array.isArray(patients) || patients.length === 0) {
            patientsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="empty-state">
                        No patients found
                    </td>
                </tr>
            `;
            return;
        }

        patientsTableBody.innerHTML = patients.map(patient => `
            <tr>
                <td>${escapeHtml(patient.id)}</td>
                <td>${escapeHtml(patient.name)}</td>
                <td>${escapeHtml(patient.age)}</td>
                <td>${escapeHtml(patient.gender)}</td>
                <td>${escapeHtml(patient.phone || "-")}</td>
                <td>${escapeHtml(patient.disease || "-")}</td>
                <td>
                    <div class="action-group">
                        <button
                            class="btn small primary"
                            onclick="editPatient(${patient.id})"
                        >
                            Edit
                        </button>

                        <button
                            class="btn small danger"
                            onclick="deletePatient(${patient.id})"
                        >
                            Delete
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");

    } catch (error) {
        patientsTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="error-text">
                    ${escapeHtml(getErrorMessage(error))}
                </td>
            </tr>
        `;
    }
}


async function editPatient(patientId) {
    try {
        const patient = await apiRequest(
            `/patients/${patientId}`
        );

        openPatientForm(patient);

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


async function deletePatient(patientId) {
    const confirmed = confirm(
        "Are you sure you want to delete this patient?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/patients/${patientId}`,
            {
                method: "DELETE"
            }
        );

        await loadPatients();
        await loadDashboard();

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


if (refreshPatients) {
    refreshPatients.addEventListener(
        "click",
        loadPatients
    );
}


if (patientForm) {
    patientForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        clearMessage(patientFormMessage);

        const payload = {
            name: patientName?.value.trim(),
            age: Number(patientAge?.value),
            gender: patientGender?.value,
            phone: patientPhone?.value.trim(),
            disease: patientDisease?.value.trim()
        };

        if (
            !payload.name ||
            !payload.age ||
            !payload.gender ||
            !payload.phone ||
            !payload.disease
        ) {
            showMessage(
                patientFormMessage,
                "Please fill all patient fields",
                "error"
            );
            return;
        }

        try {
            if (editingPatientId) {
                await apiRequest(
                    `/patients/${editingPatientId}`,
                    {
                        method: "PUT",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    patientFormMessage,
                    "Patient updated successfully",
                    "success"
                );

            } else {
                await apiRequest(
                    "/patients",
                    {
                        method: "POST",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    patientFormMessage,
                    "Patient added successfully",
                    "success"
                );
            }

            await loadPatients();
            await loadDashboard();

            setTimeout(() => {
                resetPatientForm();
            }, 700);

        } catch (error) {
            showMessage(
                patientFormMessage,
                getErrorMessage(error),
                "error"
            );
        }
    });
}


/* =========================================================
   DOCTOR FORM
   ========================================================= */

function resetDoctorForm() {
    editingDoctorId = null;

    if (editingDoctorIdInput) {
        editingDoctorIdInput.value = "";
    }

    if (doctorFormTitle) {
        doctorFormTitle.textContent = "Add Doctor";
    }

    if (doctorForm) {
        doctorForm.reset();
    }

    clearMessage(doctorFormMessage);

    if (doctorFormCard) {
        doctorFormCard.classList.add("hidden");
    }
}


function openDoctorForm(doctor = null) {
    clearMessage(doctorFormMessage);

    if (doctorFormCard) {
        doctorFormCard.classList.remove("hidden");
    }

    if (!doctor) {
        editingDoctorId = null;

        if (doctorFormTitle) {
            doctorFormTitle.textContent = "Add Doctor";
        }

        if (doctorForm) {
            doctorForm.reset();
        }

        return;
    }

    editingDoctorId = doctor.id;

    if (editingDoctorIdInput) {
        editingDoctorIdInput.value = doctor.id;
    }

    if (doctorFormTitle) {
        doctorFormTitle.textContent = "Edit Doctor";
    }

    if (doctorName) {
        doctorName.value = doctor.name || "";
    }

    if (doctorSpecialisation) {
        doctorSpecialisation.value =
            doctor.specialisation || "";
    }

    if (doctorPhone) {
        doctorPhone.value = doctor.phone || "";
    }
}


if (showDoctorFormBtn) {
    showDoctorFormBtn.addEventListener("click", () => {
        openDoctorForm();
    });
}


if (cancelDoctorBtn) {
    cancelDoctorBtn.addEventListener(
        "click",
        resetDoctorForm
    );
}


/* =========================================================
   DOCTOR CRUD
   ========================================================= */

async function loadDoctors() {
    if (!doctorsTableBody) return;

    doctorsTableBody.innerHTML = `
        <tr>
            <td colspan="5" class="loading">
                Loading doctors...
            </td>
        </tr>
    `;

    try {
        const doctors = await apiRequest("/doctors");

        if (!Array.isArray(doctors) || doctors.length === 0) {
            doctorsTableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        No doctors found
                    </td>
                </tr>
            `;
            return;
        }

        doctorsTableBody.innerHTML = doctors.map(doctor => `
            <tr>
                <td>${escapeHtml(doctor.id)}</td>
                <td>${escapeHtml(doctor.name)}</td>
                <td>${escapeHtml(doctor.specialisation)}</td>
                <td>${escapeHtml(doctor.phone || "-")}</td>
                <td>
                    <div class="action-group">
                        <button
                            class="btn small primary"
                            onclick="editDoctor(${doctor.id})"
                        >
                            Edit
                        </button>

                        <button
                            class="btn small danger"
                            onclick="deleteDoctor(${doctor.id})"
                        >
                            Delete
                        </button>

                        <button
                            class="btn small secondary"
                            onclick="viewWorkingHours(${doctor.id})"
                        >
                            Working Hours
                        </button>
                    </div>
                </td>
            </tr>
        `).join("");

    } catch (error) {
        doctorsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="error-text">
                    ${escapeHtml(getErrorMessage(error))}
                </td>
            </tr>
        `;
    }
}


async function editDoctor(doctorId) {
    try {
        const doctor = await apiRequest(
            `/doctors/${doctorId}`
        );

        openDoctorForm(doctor);

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


async function deleteDoctor(doctorId) {
    const confirmed = confirm(
        "Are you sure you want to delete this doctor?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/doctors/${doctorId}`,
            {
                method: "DELETE"
            }
        );

        await loadDoctors();
        await loadWorkingHoursDoctors();
        await loadDashboard();

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


if (refreshDoctors) {
    refreshDoctors.addEventListener(
        "click",
        loadDoctors
    );
}


if (doctorForm) {
    doctorForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        clearMessage(doctorFormMessage);

        const payload = {
            name: doctorName?.value.trim(),
            specialisation: doctorSpecialisation?.value.trim(),
            phone: doctorPhone?.value.trim()
        };

        if (
            !payload.name ||
            !payload.specialisation ||
            !payload.phone
        ) {
            showMessage(
                doctorFormMessage,
                "Please fill all doctor fields",
                "error"
            );
            return;
        }

        try {
            if (editingDoctorId) {
                await apiRequest(
                    `/doctors/${editingDoctorId}`,
                    {
                        method: "PUT",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    doctorFormMessage,
                    "Doctor updated successfully",
                    "success"
                );

            } else {
                await apiRequest(
                    "/doctors",
                    {
                        method: "POST",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    doctorFormMessage,
                    "Doctor added successfully",
                    "success"
                );
            }

            await loadDoctors();
            await loadWorkingHoursDoctors();
            await loadDashboard();

            setTimeout(() => {
                resetDoctorForm();
            }, 700);

        } catch (error) {
            showMessage(
                doctorFormMessage,
                getErrorMessage(error),
                "error"
            );
        }
    });
}


/* =========================================================
   WORKING HOURS — DOCTOR DROPDOWN
   ========================================================= */

async function loadWorkingHoursDoctors() {
    if (!workingDoctor) return;

    try {
        const doctors = await apiRequest("/doctors");

        workingDoctor.innerHTML = `
            <option value="">
                Select Doctor
            </option>
        `;

        if (!Array.isArray(doctors)) {
            return;
        }

        doctors.forEach(doctor => {
            const option = document.createElement("option");

            option.value = doctor.id;
            option.textContent =
                `${doctor.name} (ID: ${doctor.id})`;

            workingDoctor.appendChild(option);
        });

    } catch (error) {
        showMessage(
            workingHoursMessage,
            getErrorMessage(error),
            "error"
        );
    }
}


/* =========================================================
   WORKING HOURS — LOAD
   ========================================================= */

async function loadWorkingHours(doctorId) {
    if (!workingHoursTableBody || !doctorId) {
        return;
    }

    workingHoursTableBody.innerHTML = `
        <tr>
            <td colspan="5" class="loading">
                Loading working hours...
            </td>
        </tr>
    `;

    try {
        const workingHours = await apiRequest(
            `/doctors/${doctorId}/working-hours`
        );

        if (
            !Array.isArray(workingHours) ||
            workingHours.length === 0
        ) {
            workingHoursTableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        No working hours found
                    </td>
                </tr>
            `;
            return;
        }

        workingHoursTableBody.innerHTML =
            workingHours.map(item => `
                <tr>
                    <td>${escapeHtml(item.id)}</td>

                    <td>
                        ${escapeHtml(
                            getDayName(item.day_of_week)
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            formatTime(item.start_time)
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            formatTime(item.end_time)
                        )}
                    </td>

                    <td>
                        <div class="action-group">
                            <button
                                class="btn small primary"
                                onclick="editWorkingHours(
                                    ${item.id},
                                    ${item.doctor_id},
                                    ${item.day_of_week},
                                    '${item.start_time}',
                                    '${item.end_time}'
                                )"
                            >
                                Edit
                            </button>

                            <button
                                class="btn small danger"
                                onclick="deleteWorkingHours(
                                    ${item.doctor_id},
                                    ${item.id}
                                )"
                            >
                                Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `).join("");

    } catch (error) {
        workingHoursTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="error-text">
                    ${escapeHtml(getErrorMessage(error))}
                </td>
            </tr>
        `;
    }
}


/* =========================================================
   WORKING HOURS — VIEW
   ========================================================= */

async function viewWorkingHours(doctorId) {
    if (workingDoctor) {
        workingDoctor.value = String(doctorId);
    }

    await loadWorkingHours(doctorId);

    const workingSection =
        document.getElementById("workingHoursSection");

    if (workingSection) {
        workingSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}


/* =========================================================
   WORKING HOURS — CREATE / UPDATE
   ========================================================= */

if (workingHoursForm) {
    workingHoursForm.addEventListener(
        "submit",
        async (event) => {
            event.preventDefault();

            clearMessage(workingHoursMessage);

            const doctorId = workingDoctor?.value;
            const day = Number(workingDay?.value);
            const startTime = workingStartTime?.value;
            const endTime = workingEndTime?.value;

            if (
                !doctorId ||
                !day ||
                !startTime ||
                !endTime
            ) {
                showMessage(
                    workingHoursMessage,
                    "Please fill all working hours fields",
                    "error"
                );
                return;
            }

            if (startTime >= endTime) {
                showMessage(
                    workingHoursMessage,
                    "End time must be after start time",
                    "error"
                );
                return;
            }

            const payload = {
                day_of_week: day,
                start_time: startTime,
                end_time: endTime
            };

            try {
                if (editingWorkingHoursId) {
                    await apiRequest(
                        `/doctors/${doctorId}/working-hours/${editingWorkingHoursId}`,
                        {
                            method: "PUT",
                            body: JSON.stringify(payload)
                        }
                    );

                    showMessage(
                        workingHoursMessage,
                        "Working hours updated successfully",
                        "success"
                    );

                } else {
                    await apiRequest(
                        `/doctors/${doctorId}/working-hours`,
                        {
                            method: "POST",
                            body: JSON.stringify(payload)
                        }
                    );

                    showMessage(
                        workingHoursMessage,
                        "Working hours added successfully",
                        "success"
                    );
                }

                await loadWorkingHours(doctorId);

                editingWorkingHoursId = null;

                if (cancelWorkingEditBtn) {
                    cancelWorkingEditBtn.classList.add("hidden");
                }

                setTimeout(() => {
                    if (workingHoursForm) {
                        workingHoursForm.reset();
                    }

                    editingWorkingHoursId = null;
                }, 700);

            } catch (error) {
                showMessage(
                    workingHoursMessage,
                    getErrorMessage(error),
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   WORKING HOURS — EDIT
   ========================================================= */

function editWorkingHours(
    id,
    doctorId,
    day,
    startTime,
    endTime
) {
    editingWorkingHoursId = id;

    if (workingDoctor) {
        workingDoctor.value = String(doctorId);
    }

    if (workingDay) {
        workingDay.value = String(day);
    }

    if (workingStartTime) {
        workingStartTime.value =
            String(startTime).substring(0, 5);
    }

    if (workingEndTime) {
        workingEndTime.value =
            String(endTime).substring(0, 5);
    }

    if (cancelWorkingEditBtn) {
        cancelWorkingEditBtn.classList.remove("hidden");
    }

    clearMessage(workingHoursMessage);
}


/* =========================================================
   WORKING HOURS — DELETE
   ========================================================= */

async function deleteWorkingHours(
    doctorId,
    workingHoursId
) {
    const confirmed = confirm(
        "Are you sure you want to delete these working hours?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/doctors/${doctorId}/working-hours/${workingHoursId}`,
            {
                method: "DELETE"
            }
        );

        await loadWorkingHours(doctorId);

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


if (cancelWorkingEditBtn) {
    cancelWorkingEditBtn.addEventListener(
        "click",
        () => {
            editingWorkingHoursId = null;

            if (workingHoursForm) {
                workingHoursForm.reset();
            }

            cancelWorkingEditBtn.classList.add("hidden");

            clearMessage(workingHoursMessage);
        }
    );
}


/* =========================================================
   WORKING HOURS — DOCTOR CHANGE
   ========================================================= */

if (workingDoctor) {
    workingDoctor.addEventListener(
        "change",
        async () => {
            const doctorId = workingDoctor.value;

            editingWorkingHoursId = null;

            if (cancelWorkingEditBtn) {
                cancelWorkingEditBtn.classList.add("hidden");
            }

            if (doctorId) {
                await loadWorkingHours(doctorId);
            } else if (workingHoursTableBody) {
                workingHoursTableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="empty-state">
                            Select a doctor to view working hours
                        </td>
                    </tr>
                `;
            }
        }
    );
}


/* =========================================================
   APPOINTMENT DROPDOWNS — PATIENTS
   ========================================================= */

async function loadAppointmentPatients() {
    if (!appointmentPatient) {
        return;
    }

    try {
        const patients = await apiRequest("/patients");

        appointmentPatients =
            Array.isArray(patients) ? patients : [];

        appointmentPatient.innerHTML = `
            <option value="">
                Select Patient
            </option>
        `;

        appointmentPatients.forEach(patient => {
            const option =
                document.createElement("option");

            option.value = patient.id;

            option.textContent =
                `${patient.name} (ID: ${patient.id})`;

            appointmentPatient.appendChild(option);
        });

    } catch (error) {
        showMessage(
            appointmentFormMessage,
            getErrorMessage(error),
            "error"
        );
    }
}


/* =========================================================
   APPOINTMENT DROPDOWNS — DOCTORS
   ========================================================= */

async function loadAppointmentDoctors() {
    if (!appointmentDoctor) {
        return;
    }

    try {
        const doctors = await apiRequest("/doctors");

        appointmentDoctors =
            Array.isArray(doctors) ? doctors : [];

        appointmentDoctor.innerHTML = `
            <option value="">
                Select Doctor
            </option>
        `;

        appointmentDoctors.forEach(doctor => {
            const option =
                document.createElement("option");

            option.value = doctor.id;

            option.textContent =
                `${doctor.name} - ${doctor.specialisation}`;

            appointmentDoctor.appendChild(option);
        });

    } catch (error) {
        showMessage(
            appointmentFormMessage,
            getErrorMessage(error),
            "error"
        );
    }
}


/* =========================================================
   APPOINTMENT CRUD — LOAD
   ========================================================= */

async function loadAppointments() {
    if (!appointmentsTableBody) {
        return;
    }

    appointmentsTableBody.innerHTML = `
        <tr>
            <td colspan="9" class="loading">
                Loading appointments...
            </td>
        </tr>
    `;

    try {
        const appointments =
            await apiRequest("/appointments/");

        if (
            !Array.isArray(appointments) ||
            appointments.length === 0
        ) {
            appointmentsTableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="empty-state">
                        No appointments found
                    </td>
                </tr>
            `;
            return;
        }

        appointmentsTableBody.innerHTML =
            appointments.map(appointment => {

                const patient =
                    appointmentPatients.find(
                        item =>
                            Number(item.id) ===
                            Number(appointment.patient_id)
                    );

                const doctor =
                    appointmentDoctors.find(
                        item =>
                            Number(item.id) ===
                            Number(appointment.doctor_id)
                    );

                const status =
                    appointment.status || "Active";

                const statusClass =
                    getStatusClass(status);

                return `
                    <tr>
                        <td>
                            ${escapeHtml(appointment.id)}
                        </td>

                        <td>
                            ${escapeHtml(
                                patient?.name ||
                                `Patient #${appointment.patient_id}`
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                doctor?.name ||
                                `Doctor #${appointment.doctor_id}`
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                formatDate(
                                    appointment.appointment_date
                                )
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                formatTime(
                                    appointment.start_time
                                )
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                appointment.duration_minutes
                            )} min
                        </td>

                        <td>
                            ${escapeHtml(
                                appointment.reason || "-"
                            )}
                        </td>

                        <td>
                            <span
                                class="status-badge ${statusClass}"
                            >
                                ${escapeHtml(status)}
                            </span>
                        </td>

                        <td>
                            <div class="action-group">

                                <button
                                    class="btn small warning"
                                    onclick="openRescheduleModal(
                                        ${appointment.id},
                                        '${appointment.appointment_date}',
                                        '${appointment.start_time}',
                                        ${appointment.duration_minutes}
                                    )"
                                >
                                    Reschedule
                                </button>

                                ${
                                    String(status).toLowerCase()
                                    !== "cancelled"
                                    ? `
                                    <button
                                        class="btn small danger"
                                        onclick="cancelAppointment(
                                            ${appointment.id}
                                        )"
                                    >
                                        Cancel
                                    </button>
                                    `
                                    : ""
                                }

                                <button
                                    class="btn small secondary"
                                    onclick="deleteAppointment(
                                        ${appointment.id}
                                    )"
                                >
                                    Delete
                                </button>

                            </div>
                        </td>
                    </tr>
                `;
            }).join("");

    } catch (error) {
        appointmentsTableBody.innerHTML = `
            <tr>
                <td colspan="9" class="error-text">
                    ${escapeHtml(getErrorMessage(error))}
                </td>
            </tr>
        `;
    }
}


if (refreshAppointments) {
    refreshAppointments.addEventListener(
        "click",
        async () => {
            await loadAppointmentPatients();
            await loadAppointmentDoctors();
            await loadAppointments();
        }
    );
}


/* =========================================================
   APPOINTMENT CREATE
   ========================================================= */

if (appointmentForm) {
    appointmentForm.addEventListener(
        "submit",
        async (event) => {
            event.preventDefault();

            clearMessage(appointmentFormMessage);

            const patientId =
                Number(appointmentPatient?.value);

            const doctorId =
                Number(appointmentDoctor?.value);

            const appointmentDate =
                appointmentDateInputValue();

            const startTime =
                appointmentStartTime?.value;

            const duration =
                Number(appointmentDuration?.value);

            const reason =
                appointmentReason?.value.trim();

            if (
                !patientId ||
                !doctorId ||
                !appointmentDate ||
                !startTime ||
                !duration ||
                !reason
            ) {
                showMessage(
                    appointmentFormMessage,
                    "Please fill all appointment fields",
                    "error"
                );
                return;
            }

            const payload = {
                patient_id: patientId,
                doctor_id: doctorId,
                appointment_date: appointmentDate,
                start_time: startTime,
                duration_minutes: duration,
                reason
            };

            try {
                await apiRequest(
                    "/appointments/",
                    {
                        method: "POST",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    appointmentFormMessage,
                    "Appointment created successfully",
                    "success"
                );

                appointmentForm.reset();

                await loadAppointments();
                await loadDashboard();

            } catch (error) {
                showMessage(
                    appointmentFormMessage,
                    getErrorMessage(error),
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   APPOINTMENT DATE HELPER
   ========================================================= */

function appointmentDateInputValue() {
    if (!appointmentDate) {
        return "";
    }

    return appointmentDate.value;
}

/* =========================================================
   APPOINTMENT — CANCEL
   ========================================================= */

async function cancelAppointment(appointmentId) {
    const confirmed = confirm(
        "Are you sure you want to cancel this appointment?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/appointments/${appointmentId}/cancel`,
            {
                method: "PUT"
            }
        );

        await loadAppointments();
        await loadDashboard();

        alert("Appointment cancelled successfully");

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


/* =========================================================
   APPOINTMENT — DELETE
   ========================================================= */

async function deleteAppointment(appointmentId) {
    const confirmed = confirm(
        "Are you sure you want to permanently delete this appointment?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/appointments/${appointmentId}`,
            {
                method: "DELETE"
            }
        );

        await loadAppointments();
        await loadDashboard();

        alert("Appointment deleted successfully");

    } catch (error) {
        alert(getErrorMessage(error));
    }
}


/* =========================================================
   RESCHEDULE MODAL
   ========================================================= */

function openRescheduleModal(
    appointmentId,
    date,
    startTime,
    duration
) {
    if (!rescheduleModal) {
        return;
    }

    if (rescheduleAppointmentId) {
        rescheduleAppointmentId.value =
            appointmentId;
    }

    if (rescheduleDate) {
        /*
         * Backend date ko YYYY-MM-DD format mein expect karta hai.
         * Agar datetime format aaye to sirf date part lenge.
         */
        rescheduleDate.value =
            String(date).substring(0, 10);
    }

    if (rescheduleStartTime) {
        rescheduleStartTime.value =
            String(startTime).substring(0, 5);
    }

    if (rescheduleDuration) {
        rescheduleDuration.value =
            duration || "";
    }

    clearMessage(rescheduleMessage);

    rescheduleModal.classList.remove("hidden");
}


function closeReschedule() {
    if (!rescheduleModal) {
        return;
    }

    rescheduleModal.classList.add("hidden");

    if (rescheduleForm) {
        rescheduleForm.reset();
    }

    clearMessage(rescheduleMessage);
}


if (closeRescheduleModal) {
    closeRescheduleModal.addEventListener(
        "click",
        closeReschedule
    );
}


/*
 * Modal ke bahar click karne par modal close.
 */
if (rescheduleModal) {
    rescheduleModal.addEventListener(
        "click",
        (event) => {
            if (event.target === rescheduleModal) {
                closeReschedule();
            }
        }
    );
}


/* =========================================================
   RESCHEDULE SUBMIT
   ========================================================= */

if (rescheduleForm) {
    rescheduleForm.addEventListener(
        "submit",
        async (event) => {
            event.preventDefault();

            clearMessage(rescheduleMessage);

            const appointmentId =
                Number(rescheduleAppointmentId?.value);

            const newDate =
                rescheduleDate?.value;

            const newStartTime =
                rescheduleStartTime?.value;

            const newDuration =
                Number(rescheduleDuration?.value);

            if (
                !appointmentId ||
                !newDate ||
                !newStartTime ||
                !newDuration
            ) {
                showMessage(
                    rescheduleMessage,
                    "Please fill all reschedule fields",
                    "error"
                );
                return;
            }

            const payload = {
                appointment_date: newDate,
                start_time: newStartTime,
                duration_minutes: newDuration
            };

            try {
                /*
                 * Important:
                 * Backend pehle validation karega.
                 * Agar new slot invalid hua to original
                 * appointment unchanged rahegi.
                 */
                await apiRequest(
                    `/appointments/${appointmentId}/reschedule`,
                    {
                        method: "PUT",
                        body: JSON.stringify(payload)
                    }
                );

                showMessage(
                    rescheduleMessage,
                    "Appointment rescheduled successfully",
                    "success"
                );

                await loadAppointments();
                await loadDashboard();

                setTimeout(() => {
                    closeReschedule();
                }, 700);

            } catch (error) {
                /*
                 * Backend ka exact error user ko dikhayenge.
                 * Example:
                 * - Doctor already has appointment
                 * - Doctor is not available on this day
                 * - Appointment cannot be scheduled in the past
                 */
                showMessage(
                    rescheduleMessage,
                    getErrorMessage(error),
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   APPOINTMENT FORM — DOCTOR CHANGE
   ========================================================= */

if (appointmentDoctor) {
    appointmentDoctor.addEventListener(
        "change",
        async () => {
            const doctorId =
                appointmentDoctor.value;

            if (!doctorId) {
                return;
            }

            /*
             * Doctor change hone par working hours
             * frontend mein bhi fetch kar sakte hain.
             * Actual validation backend karega.
             */
            try {
                await apiRequest(
                    `/doctors/${doctorId}/working-hours`
                );
            } catch (error) {
                showMessage(
                    appointmentFormMessage,
                    getErrorMessage(error),
                    "error"
                );
            }
        }
    );
}


/* =========================================================
   DATE MINIMUM — APPOINTMENT
   ========================================================= */

function setMinimumAppointmentDate() {
    const today =
        new Date().toISOString().split("T")[0];

    if (appointmentDate) {
        appointmentDate.min = today;
    }

    if (rescheduleDate) {
        rescheduleDate.min = today;
    }
}


/* =========================================================
   INITIAL DATA LOAD
   ========================================================= */

async function initializeApplication() {
    if (!accessToken) {
        if (loginPage) {
            loginPage.classList.remove("hidden");
        }

        if (appPage) {
            appPage.classList.add("hidden");
        }

        return;
    }

    /*
     * Token localStorage mein hai,
     * isliye user ko directly application dikha sakte hain.
     */
    showApplication();

    setMinimumAppointmentDate();
}


/* =========================================================
   WINDOW GLOBAL FUNCTIONS
   ========================================================= */

/*
 * HTML ke inline onclick handlers in functions ko
 * window object ke through access karenge.
 */

window.editPatient = editPatient;
window.deletePatient = deletePatient;

window.editDoctor = editDoctor;
window.deleteDoctor = deleteDoctor;
window.viewWorkingHours = viewWorkingHours;

window.editWorkingHours = editWorkingHours;
window.deleteWorkingHours = deleteWorkingHours;

window.cancelAppointment = cancelAppointment;
window.deleteAppointment = deleteAppointment;

window.openRescheduleModal =
    openRescheduleModal;


/* =========================================================
   PAGE LOAD
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    async () => {
        setMinimumAppointmentDate();

        await initializeApplication();
    }
);