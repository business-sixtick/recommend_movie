package com.recommend.movie.springbootdeveloper.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.recommend.movie.springbootdeveloper.dto.CreateAccessTokenRequest;
import com.recommend.movie.springbootdeveloper.dto.CreateAccessTokenResponse;
import com.recommend.movie.springbootdeveloper.service.TokenService;

@RequiredArgsConstructor
@RestController
public class TokenApiController {
    private final TokenService tokenService;

    @PostMapping("/api/token")
    public ResponseEntity<CreateAccessTokenResponse> createNewAccessToken(
            @RequestBody CreateAccessTokenRequest request){
                String newAccessToken = tokenService.createNewAccessToken(request
                .getRefreshToken()); //포스트 요청이 오면 리프레시 기반의 새로운 토큰을 생성성

                return ResponseEntity.status(HttpStatus.CREATED)
                .body(new CreateAccessTokenResponse(newAccessToken));
    }
}
