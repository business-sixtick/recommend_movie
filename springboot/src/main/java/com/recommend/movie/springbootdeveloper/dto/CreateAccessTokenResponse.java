package com.recommend.movie.springbootdeveloper.dto;
// 토큰 생성 응답을 담당한다다
import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
@Getter
public class CreateAccessTokenResponse {
    private String accessToken;
}
