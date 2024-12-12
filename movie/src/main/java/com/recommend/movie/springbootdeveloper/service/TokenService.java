package com.recommend.movie.springbootdeveloper.service;

import java.time.Duration;

import org.springframework.stereotype.Service;

import com.recommend.movie.springbootdeveloper.config.jwt.TokenProvider;
import com.recommend.movie.springbootdeveloper.domain.User;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class TokenService {
    
    private final TokenProvider tokenProvider;
    private final RefreshTokenService refreshTokenService;
    private final UserService userService;

    public String createNewAccessToken(String refreshToken){
        if(!tokenProvider.validToken(refreshToken)){
            //전달받은 리프레시 토큰으로 유효성을 검사한다다
            throw new IllegalArgumentException("unexpected token");
            //실패할 시 예외 발생생
        }

    Long userId = refreshTokenService.findByRefreshToken(refreshToken).getUserId();
    User user = userService.findById(userId);

    return tokenProvider.generateToken(user, Duration.ofHours(2));
    //새로운 엑세스 토큰을 생성한다
    }
}
