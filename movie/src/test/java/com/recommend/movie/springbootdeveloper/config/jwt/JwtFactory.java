package com.recommend.movie.springbootdeveloper.config.jwt;
//jwt 토큰 서비스를 테스트하는데 사용할 모킹 객체

//테스트를 하면 진짜를 대신하는 가짜 객체

import io.jsonwebtoken.Header;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import lombok.Getter;
import lombok.Builder;

import java.time.Duration;
import java.util.Date;
import java.util.Map;

import static java.util.Collections.emptyMap;

@Getter
public class JwtFactory {

    private String subject = "test@email.com";
    private Date issuedAt = new Date();
    private Date expiration = new Date(new Date().getTime() + Duration.ofDays(14).toMillis());
    private Map<String, Object> claims = emptyMap();

    // 빌드패턴을 이용한 생성자
    @Builder
    public JwtFactory(String subject, Date issuedAt, Date expiration, Map<String, Object> claims) {
        this.subject = subject != null ? subject : this.subject;
        this.issuedAt = issuedAt != null ? issuedAt : this.issuedAt;
        this.expiration = expiration != null ? expiration : this.expiration;
        this.claims = claims != null ? claims : this.claims;
    }

    public static JwtFactory withDefaultValues() {
        return JwtFactory.builder().build();
    }

    // 라이브러리를 이용한 JWT 토큰 생성
    public String createToken(JwtProperties jwtProperties) {
        byte[] secretKey = jwtProperties.getDecodedSecretKey(); // 디코딩된 키 사용

        return Jwts.builder()
                .setSubject(subject)
                .setHeaderParam(Header.TYPE, Header.JWT_TYPE)
                .setIssuer(jwtProperties.getIssuer())
                .setIssuedAt(issuedAt)
                .setExpiration(expiration)
                .addClaims(claims)
                // .signWith(SignatureAlgorithm.HS256, jwtProperties.getSecretKey())
                .signWith(SignatureAlgorithm.HS256, secretKey)
                .compact();
    }
}
