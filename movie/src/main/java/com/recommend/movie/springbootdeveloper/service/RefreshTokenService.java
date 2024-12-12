package com.recommend.movie.springbootdeveloper.service;

import org.springframework.stereotype.Service;

import com.recommend.movie.springbootdeveloper.domain.RefreshToken;
import com.recommend.movie.springbootdeveloper.repository.RefreshTokenRepository;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class RefreshTokenService {
    private final RefreshTokenRepository refreshTokenRepository;

    public RefreshToken findByRefreshToken(String refreshToken){
        return refreshTokenRepository.findByRefreshToken(refreshToken)
        //새로 만들어 전달받은 리프레시 토큰으로 토큰 객체를 검색색
            .orElseThrow(() -> new IllegalArgumentException("unexpected token"));
    }
}
