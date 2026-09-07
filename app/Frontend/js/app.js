// =========================================================
// HOSPITAL MANAGEMENT FRONTEND
// Saara frontend logic ek hi JS file mein rakha gaya hai.
// HTML = structure
// CSS  = design
// JS   = API calls + interaction + page logic
// =========================================================


// =========================================================
// API CONFIG
// =========================================================

// FastAPI backend ka base URL.
// Agar backend ka address/port change ho to sirf yahan change karna hai.
const API_BASE_URL = "http://127.0.0.1:8000";


// =========================================================
// DOM ELEMENTS
// =========================================================

// HTML ke important elements ko variables mein store kar rahe hain.
// Isse baar-baar document.getElementById() likhne ki zarurat nahi padegi.

const loginPage = document.getElementById("loginPage");
const appPage = document.getElementById("appPage");

const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");
const loggedInUser = document.getElementById("loggedInUser");

const pageTitle = document.getElementById("pageTitle");

const patientCount = document.getElementById("patientCount");
const doctorCount = document.getElementById("doctorCount");
const appointmentCount = document.getElementById("appointmentCount");

const patientsTableBody = document.getElementById("patientsTableBody");
const doctorsTableBody = document.getElementById("doctorsTableBody");
const appointmentsTableBody = document.getElementById("appointmentsTableBody");

const patientFormCard = document.getElementById("patientFormCard");
const patientForm = document.getElementById("patientForm");
const patientFormMessage = document.getElementById("patientFormMessage");


// =========================================================
// AUTHENTICATION HELPERS
// =========================================================

// Login ke baad JWT token browser ke localStorage mein save karte hain.
// localStorage page refresh ke baad bhi token ko temporarily preserve karta hai.

function saveToken(token) {
    localStorage.setItem("access_token", token);
}


// Saved JWT token nikalna.
function getToken() {
    return localStorage.getItem("access_token");
}


// Current logged-in username save karna.
function saveUsername(username) {
    localStorage.setItem("username", username);
}


// Username retrieve karna.
function getUsername() {
    return localStorage.getItem("username");
}


// Logout par token aur username clear karna.
function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");

    // Login screen wapas show karna.
    showLoginPage();
}


// =========================================================
// API REQUEST HELPER
// =========================================================

// Ye common helper function hai.
// Iske through GET/POST/PUT/DELETE requests bhejna easy ho jata hai.
//
// Example:
// apiRequest("/patients")
// apiRequest("/patients", { method: "POST", body: JSON.stringify(data) })

async function apiRequest(endpoint, options = {}) {

    const token = getToken();

    const headers = {
        "Content-Type": "application/json",
        ...options.headers
    };

    // Agar token available hai to Authorization header add karenge.
    // Abhi tumhare patient/doctor endpoints protected nahi hain,
    // lekin future authentication ke liye ye ready rakha hai.
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    // 204 No Content mein JSON response nahi hota.
    if (response.status === 204) {
        return null;
    }

    // Server ka response JSON mein convert karna.
    const data = await response.json();

    // Agar backend ne error status diya hai,
    // to error ko readable message ke saath throw karenge.
    if (!response.ok) {
        throw new Error(
            data.detail || "Something went wrong"
        );
    }

    return data;
}


// =========================================================
// LOGIN
// =========================================================

// Login form submit hone par ye function chalega.

loginForm.addEventListener("submit", async function (event) {

    // Default form submit ko rok rahe hain.
    // Warna browser page reload kar deta.
    event.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    loginMessage.textContent = "Logging in...";
    loginMessage.className = "message";

    try {

        // FastAPI ke /auth/login endpoint ko POST request.
        const data = await apiRequest(
            "/auth/login",
            {
                method: "POST",
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        // Backend se mila JWT save karna.
        saveToken(data.access_token);

        // Username bhi save kar dete hain taaki dashboard par dikha sakein.
        saveUsername(username);

        loginMessage.textContent = "";

        // Login ke baad dashboard open.
        showAppPage();

    } catch (error) {

        // Backend se aaya error user ko show karna.
        loginMessage.textContent = error.message;
        loginMessage.className = "message error";
    }
});


// =========================================================
// PAGE VISIBILITY
// =========================================================

// Login screen show karna.
function showLoginPage() {
    loginPage.classList.remove("hidden");
    appPage.classList.add("hidden");
}


// Main application show karna.
function showAppPage() {
    loginPage.classList.add("hidden");
    appPage.classList.remove("hidden");

    loggedInUser.textContent = getUsername() || "User";

    // Login ke baad dashboard ka data load karna.
    showSection("dashboard");
    loadDashboardData();
}


// =========================================================
// SIDEBAR NAVIGATION
// =========================================================

// Sidebar ke saare navigation buttons select kar rahe hain.
const navItems = document.querySelectorAll(".nav-item");

navItems.forEach(function (item) {

    item.addEventListener("click", function () {

        const sectionName = item.dataset.section;

        showSection(sectionName);
    });
});


// Dashboard ke "View Patients" button ke liye.
document.querySelectorAll("[data-open-section]").forEach(function (button) {

    button.addEventListener("click", function () {
        showSection(button.dataset.openSection);
    });
});


// Actual section switching function.
function showSection(sectionName) {

    // Saare sections hide karna.
    document.querySelectorAll(".page-section").forEach(function (section) {
        section.classList.remove("active-section");
    });

    // Required section show karna.
    const targetSection = document.getElementById(
        `${sectionName}Section`
    );

    if (targetSection) {
        targetSection.classList.add("active-section");
    }

    // Sidebar mein selected item ko active banana.
    navItems.forEach(function (item) {
        item.classList.toggle(
            "active",
            item.dataset.section === sectionName
        );
    });

    // Page heading update karna.
    const titles = {
        dashboard: "Dashboard",
        patients: "Patients",
        doctors: "Doctors",
        appointments: "Appointments"
    };

    pageTitle.textContent = titles[sectionName] || "Dashboard";


    // Section open hone par relevant API call.
    if (sectionName === "dashboard") {
        loadDashboardData();
    }

    if (sectionName === "patients") {
        loadPatients();
    }

    if (sectionName === "doctors") {
        loadDoctors();
    }

    if (sectionName === "appointments") {
        loadAppointments();
    }
}


// =========================================================
// PATIENTS
// =========================================================

// Backend se saare patients fetch karna.
async function loadPatients() {

    patientsTableBody.innerHTML = `
        <tr>
            <td colspan="5" class="empty-state">
                Loading patients...
            </td>
        </tr>
    `;

    try {

        // Backend endpoint: GET /patients
        const patients = await apiRequest("/patients");

        patientCount.textContent = patients.length;

        renderPatients(patients);

    } catch (error) {

        patientsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    Error: ${escapeHtml(error.message)}
                </td>
            </tr>
        `;
    }
}


// Patients ko HTML table mein display karna.
function renderPatients(patients) {

    if (!patients.length) {
        patientsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    No patients found.
                </td>
            </tr>
        `;
        return;
    }

    patientsTableBody.innerHTML = patients.map(function (patient) {

        return `
            <tr>
                <td>${patient.id}</td>
                <td>${escapeHtml(patient.name)}</td>
                <td>${patient.age}</td>
                <td>${escapeHtml(patient.gender)}</td>
                <td>${escapeHtml(patient.disease)}</td>
            </tr>
        `;

    }).join("");
}


// =========================================================
// ADD PATIENT
// =========================================================

document.getElementById("showPatientFormBtn").addEventListener(
    "click",
    function () {

        patientFormCard.classList.remove("hidden");

        // Form open hote hi name field par focus.
        document.getElementById("patientName").focus();
    }
);


document.getElementById("cancelPatientBtn").addEventListener(
    "click",
    function () {

        patientForm.reset();
        patientFormCard.classList.add("hidden");

        patientFormMessage.textContent = "";
    }
);


// Add Patient form submit.
patientForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const patientData = {
        name: document.getElementById("patientName").value.trim(),
        age: Number(document.getElementById("patientAge").value),
        gender: document.getElementById("patientGender").value,
        disease: document.getElementById("patientDisease").value.trim()
    };

    patientFormMessage.textContent = "Saving patient...";
    patientFormMessage.className = "message form-message";

    try {

        // FastAPI endpoint: POST /patients
        await apiRequest(
            "/patients",
            {
                method: "POST",
                body: JSON.stringify(patientData)
            }
        );

        patientFormMessage.textContent = "Patient added successfully.";
        patientFormMessage.className = "message success form-message";

        patientForm.reset();

        // New patient ke baad table refresh.
        await loadPatients();

        // Thodi der baad form close.
        setTimeout(function () {
            patientFormCard.classList.add("hidden");
            patientFormMessage.textContent = "";
        }, 800);

    } catch (error) {

        patientFormMessage.textContent = error.message;
        patientFormMessage.className = "message error form-message";
    }
});


// =========================================================
// DOCTORS
// =========================================================

// Backend se doctors fetch karna.
async function loadDoctors() {

    doctorsTableBody.innerHTML = `
        <tr>
            <td colspan="5" class="empty-state">
                Loading doctors...
            </td>
        </tr>
    `;

    try {

        // Backend endpoint: GET /doctors
        const doctors = await apiRequest("/doctors");

        doctorCount.textContent = doctors.length;

        renderDoctors(doctors);

    } catch (error) {

        doctorsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    Error: ${escapeHtml(error.message)}
                </td>
            </tr>
        `;
    }
}


// Doctors ko table mein render karna.
function renderDoctors(doctors) {

    if (!doctors.length) {
        doctorsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    No doctors found.
                </td>
            </tr>
        `;
        return;
    }

    doctorsTableBody.innerHTML = doctors.map(function (doctor) {

        return `
            <tr>
                <td>${doctor.id}</td>
                <td>${escapeHtml(doctor.name)}</td>
                <td>${escapeHtml(doctor.specialisation)}</td>
                <td>${escapeHtml(doctor.phone)}</td>
                <td>${escapeHtml(doctor.status)}</td>
            </tr>
        `;

    }).join("");
}


// =========================================================
// APPOINTMENTS
// =========================================================

// Backend se appointments fetch karna.
async function loadAppointments() {

    appointmentsTableBody.innerHTML = `
        <tr>
            <td colspan="6" class="empty-state">
                Loading appointments...
            </td>
        </tr>
    `;

    try {

        // Backend endpoint: GET /appointments/
        const appointments = await apiRequest("/appointments/");

        appointmentCount.textContent = appointments.length;

        renderAppointments(appointments);

    } catch (error) {

        appointmentsTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    Error: ${escapeHtml(error.message)}
                </td>
            </tr>
        `;
    }
}


// Appointment data ko table mein render karna.
function renderAppointments(appointments) {

    if (!appointments.length) {
        appointmentsTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    No appointments found.
                </td>
            </tr>
        `;
        return;
    }

    appointmentsTableBody.innerHTML = appointments.map(function (appointment) {

        return `
            <tr>
                <td>${appointment.id}</td>
                <td>${appointment.patient_id}</td>
                <td>${appointment.doctor_id}</td>
                <td>${formatDate(appointment.appointment_date)}</td>
                <td>${escapeHtml(appointment.reason)}</td>
                <td>${escapeHtml(appointment.status)}</td>
            </tr>
        `;

    }).join("");
}


// =========================================================
// DASHBOARD DATA
// =========================================================

// Dashboard par teen APIs ka data load karna.
async function loadDashboardData() {

    const dashboardStatus = document.getElementById("dashboardStatus");

    dashboardStatus.textContent = "Loading data from FastAPI...";

    try {

        // Teen API calls parallel mein run kar rahe hain.
        // Promise.all() ka benefit: teeno requests complete hone ka wait.
        const [patients, doctors, appointments] = await Promise.all([
            apiRequest("/patients"),
            apiRequest("/doctors"),
            apiRequest("/appointments/")
        ]);

        patientCount.textContent = patients.length;
        doctorCount.textContent = doctors.length;
        appointmentCount.textContent = appointments.length;

        dashboardStatus.textContent =
            "Backend connection successful. Data PostgreSQL-backed FastAPI API se aa raha hai.";

    } catch (error) {

        dashboardStatus.textContent =
            `Backend connection error: ${error.message}`;
    }
}


// =========================================================
// REFRESH BUTTONS
// =========================================================

document.getElementById("refreshDashboard").addEventListener(
    "click",
    loadDashboardData
);

document.getElementById("refreshPatients").addEventListener(
    "click",
    loadPatients
);

document.getElementById("refreshDoctors").addEventListener(
    "click",
    loadDoctors
);

document.getElementById("refreshAppointments").addEventListener(
    "click",
    loadAppointments
);


// =========================================================
// LOGOUT
// =========================================================

document.getElementById("logoutBtn").addEventListener(
    "click",
    logout
);


// =========================================================
// SMALL UTILITY FUNCTIONS
// =========================================================

// API se aayi date ko thoda readable format mein show karna.
function formatDate(dateString) {

    if (!dateString) {
        return "-";
    }

    const date = new Date(dateString);

    if (Number.isNaN(date.getTime())) {
        return dateString;
    }

    return date.toLocaleString();
}


// HTML injection se bachne ke liye text escape karna.
// User/API data ko directly innerHTML mein daalne se pehle
// ye helper safe text banata hai.
function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =========================================================
// INITIAL APP START
// =========================================================

// Page load hote hi check karenge ki JWT already saved hai ya nahi.

document.addEventListener("DOMContentLoaded", function () {

    const token = getToken();

    if (token) {

        // Token available hai → user ko directly dashboard dikhao.
        showAppPage();

    } else {

        // Token nahi hai → login screen dikhao.
        showLoginPage();
    }
});
