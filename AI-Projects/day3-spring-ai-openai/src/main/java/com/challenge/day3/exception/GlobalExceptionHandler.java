package com.challenge.day3.exception;

import com.challenge.day3.dto.ErrorResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Centralized exception handler for ALL controllers.
 *
 * Without this class → Spring returns a raw ugly error page.
 * With this class    → Every error returns a clean, consistent JSON response.
 *
 * Handles:
 * 1. Validation failures (@NotBlank, @Size etc.)  → 400 Bad Request
 * 2. OpenAI/runtime errors (bad key, quota etc.)  → 500 Internal Server Error
 * 3. Any unexpected exception                      → 500 Internal Server Error
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * Triggered automatically when @Valid fails on @RequestBody.
     *
     * Java 8 Stream used to:
     * - Loop over all field errors
     * - Map each to "fieldName: error message" string
     * - Collect into a List so ALL errors are returned at once
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationErrors(MethodArgumentNotValidException ex) {

        List<String> errors = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .toList();

        log.warn("Validation failed: {}", errors);

        return ResponseEntity.badRequest().body(
                ErrorResponse.builder()
                        .status(HttpStatus.BAD_REQUEST.value())
                        .error("Validation Failed")
                        .messages(errors)
                        .timestamp(LocalDateTime.now())
                        .build()
        );
    }

    /**
     * Catches OpenAI API failures — e.g. wrong API key, quota exceeded, network error.
     * Logs full stack trace on server, returns clean message to client.
     */
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<ErrorResponse> handleRuntimeException(RuntimeException ex) {
        log.error("Runtime error: {}", ex.getMessage(), ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                ErrorResponse.builder()
                        .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                        .error("AI Service Error")
                        .messages(List.of("OpenAI call failed: " + ex.getMessage()))
                        .timestamp(LocalDateTime.now())
                        .build()
        );
    }

    /**
     * Catch-all for any other unexpected exception.
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGenericException(Exception ex) {
        log.error("Unexpected error: {}", ex.getMessage(), ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(
                ErrorResponse.builder()
                        .status(HttpStatus.INTERNAL_SERVER_ERROR.value())
                        .error("Internal Server Error")
                        .messages(List.of("An unexpected error occurred."))
                        .timestamp(LocalDateTime.now())
                        .build()
        );
    }
}
