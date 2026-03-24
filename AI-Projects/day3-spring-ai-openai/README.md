# Day 3 — AI-Powered REST API with Spring AI + OpenAI (GPT)

No GCP. No CLI tools. Just an API key. ✅

---

## 🗂️ Project Structure

```
day3-spring-ai-openai/
├── src/main/java/com/challenge/day3/
│   ├── Day3Application.java                  ← Spring Boot entry point
│   ├── controller/
│   │   └── ChatController.java               ← REST endpoints
│   ├── dto/
│   │   ├── ChatRequest.java                  ← Request POJO
│   │   ├── ChatResponse.java                 ← Response POJO
│   │   └── ErrorResponse.java                ← Error POJO
│   ├── service/
│   │   └── ChatService.java                  ← OpenAI call logic
│   └── exception/
│       └── GlobalExceptionHandler.java       ← Centralized error handling
├── src/main/resources/
│   └── application.properties                ← ⚠️ Put your API key here
└── pom.xml
```

---

## ✅ Prerequisites

### 1. Java 17
```bash
java -version
# If not installed → https://adoptium.net (download Eclipse Temurin 17)
```

### 2. Maven
```bash
mvn -version
# If not installed → https://maven.apache.org/download.cgi
```

### 3. IntelliJ IDEA (recommended)
Download free Community edition → https://www.jetbrains.com/idea/download/

---

## 🔑 Get Your OpenAI API Key (2 minutes)

1. Go to → **https://platform.openai.com**
2. Sign up / Log in
3. Click your profile (top right) → **API Keys**
4. Click **"Create new secret key"**
5. Copy the key → it looks like `sk-proj-abc123...`

> 💡 New accounts get **$5 free credits** — enough for hundreds of test questions.
> `gpt-4o-mini` costs ~$0.00015 per question = basically free for learning.

---

## ⚙️ Configure the App

Open `src/main/resources/application.properties`

Change **just this one line**:
```properties
spring.ai.openai.api-key=sk-YOUR_OPENAI_API_KEY_HERE
```
Replace with your actual key. That's it. Nothing else to configure.

---

## 🚀 Run the Application

### Option A — IntelliJ IDEA (easiest)
1. Open IntelliJ → **File → Open** → select `day3-spring-ai-openai` folder
2. Wait for Maven to download dependencies (watch the bottom progress bar)
3. Open `Day3Application.java`
4. Click the ▶️ green Run button next to the `main` method
5. See `Started Day3Application on port 8080` in console → you're live!

### Option B — Terminal
```bash
cd day3-spring-ai-openai
mvn clean install -DskipTests
mvn spring-boot:run
```

App runs at → **http://localhost:8080**

---

## 🧪 Test with Postman

### Test 1 — Health Check
```
GET http://localhost:8080/api/ai/health
```
✅ Expected:
```
✅ Day 3 Spring AI + OpenAI API is running!
```

---

### Test 2 — Basic Chat (no system instruction)
```
POST http://localhost:8080/api/ai/chat
Content-Type: application/json
```
```json
{
  "question": "What is the difference between HashMap and ConcurrentHashMap in Java?"
}
```
✅ Expected:
```json
{
  "question": "What is the difference between HashMap and ConcurrentHashMap in Java?",
  "answer": "HashMap is not thread-safe and should only be used in single-threaded...",
  "modelUsed": "gpt-4o-mini",
  "respondedAt": "2025-03-14T10:30:00"
}
```

---

### Test 3 — Custom System Instruction
```json
{
  "question": "What is a Java Stream?",
  "systemInstruction": "You are a teacher explaining Java to a 10-year-old. Use simple words and a fun analogy."
}
```

---

### Test 4 — Validation Error (send blank question)
```json
{
  "question": ""
}
```
✅ Expected 400 response:
```json
{
  "status": 400,
  "error": "Validation Failed",
  "messages": ["question: Question cannot be blank"],
  "timestamp": "2025-03-14T10:30:00"
}
```

---

### Test 5 — Indian Tax Domain (real-world use case)
```json
{
  "question": "What documents do I need to file ITR-1 in India?",
  "systemInstruction": "You are an Indian chartered accountant. Give practical advice for salaried employees filing their first ITR."
}
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `Incorrect API key provided` | Wrong/expired API key | Re-generate key at platform.openai.com |
| `You exceeded your current quota` | Free credits used up | Add payment method on OpenAI dashboard |
| `Port 8080 already in use` | Another app running | Change `server.port=8081` in properties |
| `Could not resolve dependencies` | Spring milestone repo missing | Check pom.xml has the repositories section |
| `401 Unauthorized` | Key not set in properties | Double-check application.properties |

---

## 📚 Key Concepts Summary

| Concept | Where Used | Why |
|---|---|---|
| `spring-ai-starter-model-openai` | pom.xml | Auto-configures ChatModel with your API key |
| `ChatModel` | ChatService | Spring AI's abstraction over raw OpenAI HTTP API |
| `ChatClient` fluent API | ChatService | Builds prompts with `.system()` and `.user()` cleanly |
| `@Value` | ChatService | Reads model name from properties — no hardcoding |
| `Optional` (Java 8) | ChatService | Null-safe fallback for `systemInstruction` |
| Text blocks (Java 15) | ChatService | Readable multiline default system prompt |
| `@Valid` + `@NotBlank` | Controller + DTO | Rejects bad input before it reaches service layer |
| `@RestControllerAdvice` | GlobalExceptionHandler | Centralized error handling for all endpoints |
| Stream + `.toList()` | GlobalExceptionHandler | Maps field errors → clean message list |
| `@Builder` (Lombok) | All DTOs | Clean object construction without telescoping constructors |

---

## 💡 Why Spring AI over calling OpenAI directly?

Without Spring AI you'd write:
```java
// Manual approach — lots of boilerplate
HttpClient client = HttpClient.newHttpClient();
String body = """{"model":"gpt-4o-mini","messages":[{"role":"user","content":"%s"}]}""".formatted(question);
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.openai.com/v1/chat/completions"))
    .header("Authorization", "Bearer " + apiKey)
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString(body))
    .build();
// then parse response JSON manually...
```

With Spring AI:
```java
// Spring AI — clean, readable, provider-agnostic
String answer = ChatClient.create(chatModel)
    .prompt()
    .system(systemPrompt)
    .user(question)
    .call()
    .content();
```

Same result. 10x less code. Works with OpenAI, Gemini, Claude — just swap the dependency. 🚀
