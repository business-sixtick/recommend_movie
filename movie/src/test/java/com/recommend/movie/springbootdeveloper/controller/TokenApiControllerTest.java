package com.recommend.movie.springbootdeveloper.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.recommend.movie.springbootdeveloper.config.jwt.JwtFactory;
import com.recommend.movie.springbootdeveloper.config.jwt.JwtProperties;
import com.recommend.movie.springbootdeveloper.domain.RefreshToken;
import com.recommend.movie.springbootdeveloper.domain.User;
import com.recommend.movie.springbootdeveloper.dto.CreateAccessTokenRequest;
import com.recommend.movie.springbootdeveloper.repository.RefreshTokenRepository;
import com.recommend.movie.springbootdeveloper.repository.UserRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.util.Map;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class TokenApiControllerTest {

    @Autowired
    protected MockMvc mockMvc;

    @Autowired
    protected ObjectMapper objectMapper;

    @Autowired
    private WebApplicationContext context;

    @Autowired
    JwtProperties jwtProperties;

    @Autowired
    UserRepository userRepository;

    @Autowired
    RefreshTokenRepository refreshTokenRepository;

    @BeforeEach
    public void mockMvcSetUp(){
        this.mockMvc = MockMvcBuilders.webAppContextSetup(context).build();
        userRepository.deleteAll();
    }

    @DisplayName("createNewAccessToken: 새로운 토큰을 발급한다.")
    @Test
    public void createNewAccessToken() throws Exception{
        final String url = "/api/token";
        User testUser = userRepository.save(User.builder()
                        .email("user@gmail.com")
                        .password("test")
                .build()); // 유저를 등록하면 로그인이 되는건가?

        String refreshToken = JwtFactory.builder()
                .claims(Map.of("id", testUser.getId()))
                .build()
                .createToken(jwtProperties);

        refreshTokenRepository.save(new RefreshToken(testUser.getId(), refreshToken));

        CreateAccessTokenRequest request = new CreateAccessTokenRequest();
        request.setRefreshToken(refreshToken);
        final String requestBody = objectMapper.writeValueAsString(request); // json 형식으로 내보내는거였나?
        System.out.println("requestBody : " + requestBody);

        ResultActions resultActions = mockMvc.perform(post(url)
                .contentType(MediaType.APPLICATION_JSON_VALUE)
                .content(requestBody));

        resultActions.andExpect(status().isCreated())
                .andExpect(jsonPath("$.accessToken").isNotEmpty());
    }
}

// 294 페이지 테스트 미완료
