https://maven.apache.org/download.cgi# Day 3 — AI-Powered REST API with Spring AI + Google Gemini

---

## 🗂️ Project Structure

```
day3-spring-ai-gemini/
├── src/main/java/com/challenge/day3/
│   ├── Day3Application.java                  ← Spring Boot entry point
│   ├── controller/
│   │   └── ChatController.java               ← REST endpoints
│   ├── dto/
│   │   ├── ChatRequest.java                  ← Request body POJO
│   │   ├── ChatResponse.java                 ← Response body POJO
│   │   └── ErrorResponse.java                ← Error response POJO
│   ├── service/
│   │   └── ChatService.java                  ← Gemini AI call logic
│   └── exception/
│       └── GlobalExceptionHandler.java       ← Centralized error handling
├── src/main/resources/
│   └── application.properties                ← Config (set your project ID here)
├── src/test/...
└── pom.xml
```

---

## ✅ Prerequisites — Install These First

### 1. Java 17
Check if installed:
```bash
java -version
```
If not installed → https://adoptium.net (download Eclipse Temurin 17)

### 2. Maven
Check if installed:
```bash
mvn -version
```
If not installed → https://maven.apache.org/download.cgi

### 3. Google Cloud CLI (gcloud)
```bash
# macOS
brew install --cask google-cloud-sdk

# Windows → download installer from:
# https://cloud.google.com/sdk/docs/install
```

### 4. IntelliJ IDEA (recommended)
Download Community (free) version → https://www.jetbrains.com/idea/download/

---

## 🔐 Google Cloud Setup (One-Time)

### Step 1 — Create a Google Cloud Account
Go to → https://console.cloud.google.com
(New accounts get $300 free credits — Gemini API usage is very cheap)

### Step 2 — Create a Project
1. Click the project dropdown (top left in GCP Console)
2. Click **New Project**
3. Give it a name, e.g. `java-ai-challenge`
4. Note the **Project ID** (something like `java-ai-challenge-123456`)

### Step 3 — Enable the Vertex AI API
Go to → https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
Click **Enable**

### Step 4 — Login via gcloud CLI
```bash
# Initialize gcloud (first time only)
gcloud init

# Login with your Google account
gcloud auth login

# Set Application Default Credentials (this is what Spring AI uses)
gcloud auth application-default login
```
A browser window opens → login → credentials saved automatically.
Spring AI picks these up automatically — no API key string needed in code!

### Step 5 — Set your Project
```bash
gcloud config set project YOUR_PROJECT_ID
```

---

## ⚙️ Configure the App

Open this file:
```
src/main/resources/application.properties
```

Change this one line:
```properties
spring.ai.vertex.ai.gemini.project-id=YOUR_GCP_PROJECT_ID
```
Replace `YOUR_GCP_PROJECT_ID` with your actual project ID from Step 2.

---

## 🚀 Run the Application

### Option A — IntelliJ IDEA (easiest)
1. Open IntelliJ → **File → Open** → select the `day3-spring-ai-gemini` folder
2. Wait for Maven to download dependencies (bottom progress bar)
3. Open `Day3Application.java`
4. Click the ▶️ green play button next to `main` method
5. See `Started Day3Application` in console → app is running!

### Option B — Terminal / Command Line
```bash
# Navigate to project folder
cd day3-spring-ai-gemini

# Download dependencies and build
mvn clean install -DskipTests

# Run the app
mvn spring-boot:run
```

App starts on → **http://localhost:8080**

---

## 🧪 Test with Postman

### Step 1 — Health Check (confirm app is running)
```
GET http://localhost:8080/api/ai/health
```
Expected response:
```
✅ Day 3 Spring AI + Gemini API is running!
```

---

### Step 2 — Basic Chat (default system instruction)
```
POST http://localhost:8080/api/ai/chat
Content-Type: application/json
```
Body:
```json
{
  "question": "What is the difference between HashMap and ConcurrentHashMap in Java?"
}
```
Expected response:
```json
{
  "question": "What is the difference between HashMap and ConcurrentHashMap in Java?",
  "answer": "HashMap is not thread-safe...",
  "modelUsed": "gemini-2.0-flash",
  "respondedAt": "2025-03-14T10:30:00"
}
```

---

### Step 3 — Custom System Instruction
```json
{
  "question": "What is GST filing and why is it important?",
  "systemInstruction": "You are an Indian tax expert. Explain concepts in simple English for a beginner with no finance background."
}
```

---

### Step 4 — Validation Error Test
Send an empty question → should get 400 error:
```json
{
  "question": ""
}
```
Expected response:
```json
{
  "status": 400,
  "error": "Validation Failed",
  "messages": ["question: Question cannot be blank"],
  "timestamp": "2025-03-14T10:30:00"
}
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `Application Default Credentials not found` | gcloud not logged in | Run `gcloud auth application-default login` |
| `403 PERMISSION_DENIED` | Vertex AI API not enabled | Enable it at console.cloud.google.com/apis |
| `404 model not found` | Wrong model name | Use `gemini-2.0-flash` in application.properties |
| `Port 8080 already in use` | Another app using 8080 | Change `server.port=8081` in application.properties |
| `Could not resolve dependencies` | Spring AI milestone repo not added | Check pom.xml has the Spring milestone repository |

---

## 📚 Key Concepts Used

| Concept | Where used |
|---|---|
| `ChatModel` | Auto-configured by Spring AI for Gemini |
| `ChatClient` fluent API | ChatService — builds prompts cleanly |
| `Optional` (Java 8) | ChatService — null-safe systemInstruction fallback |
| Text blocks (Java 15) | DEFAULT_SYSTEM_INSTRUCTION multiline string |
| `@Valid` + `@NotBlank` | ChatController + ChatRequest — input validation |
| `@RestControllerAdvice` | GlobalExceptionHandler — centralized error handling |
| Stream + `.toList()` | GlobalExceptionHandler — maps field errors to messages |
| `@Builder` (Lombok) | ChatResponse, ErrorResponse — clean object creation |

---

## 📢 LinkedIn Summary

🚀 Day 3 of my #30DayJavaChallenge

Built an AI-powered REST API using Spring AI + Google Gemini in Java 17!

✅ Spring AI's ChatClient — no manual HTTP, no JSON parsing boilerplate
✅ System prompts to set AI personality per request
✅ @Valid + @NotBlank input validation
✅ Optional for null-safe fallback logic
✅ Centralized GlobalExceptionHandler with Stream-based error mapping

Spring AI is to AI what Spring Data is to databases — pure business logic, zero boilerplate. 🔥

#Java #SpringBoot #SpringAI #GoogleGemini #GenerativeAI #BackendDevelopment
