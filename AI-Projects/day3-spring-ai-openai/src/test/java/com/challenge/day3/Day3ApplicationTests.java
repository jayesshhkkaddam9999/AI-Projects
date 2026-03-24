package com.challenge.day3;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@TestPropertySource(properties = {
        // Dummy API key so Spring context loads without a real key during tests
        "spring.ai.openai.api-key=sk-test-dummy-key"
})
class Day3ApplicationTests {

    @Test
    void contextLoads() {
        // Verifies Spring context starts up correctly
    }
}
