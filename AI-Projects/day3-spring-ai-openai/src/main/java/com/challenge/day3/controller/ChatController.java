package com.challenge.day3.controller;

import com.challenge.day3.dto.ChatRequest;
import com.challenge.day3.dto.ChatResponse;
import com.challenge.day3.service.ChatService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST Controller exposing AI chat endpoints.
 *
 * Endpoints:
 *  GET  /api/ai/health  → Health check, confirms app is running (no AI call)
 *  POST /api/ai/chat    → Send a question, get GPT's answer
 */
@Slf4j
@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class ChatController {

    private final ChatService chatService;

    /**
     * Health check — no OpenAI call, just confirms the app is up.
     * Always test this first before running chat requests.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("✅ Day 3 Spring AI + OpenAI API is running!");
    }

    /**
     * Main chat endpoint.
     *
     * @Valid → triggers all validations on ChatRequest (@NotBlank, @Size)
     * If validation fails → GlobalExceptionHandler returns 400 with error details
     * If OpenAI fails   → GlobalExceptionHandler returns 500 with error details
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@Valid @RequestBody ChatRequest request) {
        log.info("POST /api/ai/chat");
        ChatResponse response = chatService.chat(request);
        return ResponseEntity.ok(response);
    }
}
