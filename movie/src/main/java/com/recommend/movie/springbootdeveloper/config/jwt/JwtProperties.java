package com.recommend.movie.springbootdeveloper.config.jwt;

import lombok.Getter;
import lombok.Setter;

import java.util.Base64;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Setter
@Getter
@Component
@ConfigurationProperties("jwt") // 자바 클래스에 프로퍼티값을 가져와서 사용하는 애너테이션
public class JwtProperties {
    private String issuer;
    private String secretKey;

    public byte[] getDecodedSecretKey() {
        // Base64 또는 Base64Url 디코딩
        return Base64.getDecoder().decode(secretKey);
    }
}
