package com.recommend.movie.springbootdeveloper.dto;
// 토큰 생성 요청을 담당한다

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CreateAccessTokenRequest {
    private String refreshToken;
}
