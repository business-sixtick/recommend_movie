package com.recommend.movie.springbootdeveloper.config;
//실제 인증 처리를 담당하는 시큐리티 설정 파일

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.ProviderManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityCustomizer;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;

import com.recommend.movie.springbootdeveloper.service.UserDetailService;

import static org.springframework.boot.autoconfigure.security.servlet.PathRequest.toH2Console;

@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class WebSecurityConfig {

    private final UserDetailService userService;

    // 시큐리티 비활성화  // index.html 첫페이지??
    @Bean
    public WebSecurityCustomizer configure(){
        return (web) -> web.ignoring()
            // .requestMatchers(toH2Console()) //이 메서드를 활성화하면, /h2-console/** 경로의 요청이 Spring Security 필터 체인에 걸리지 않고 바로 처리됩니다.
            .requestMatchers(new AntPathRequestMatcher("/static/**"));
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception{
        return http.authorizeRequests(auth -> auth
                .requestMatchers(new AntPathRequestMatcher("/login"),
                        new AntPathRequestMatcher("/signup"),
                        new AntPathRequestMatcher("/user"),
                        new AntPathRequestMatcher("/articles")) //
                .permitAll()
                .anyRequest().authenticated())
                .formLogin(formLogin -> formLogin
                        .loginPage("/login")
                        .defaultSuccessUrl("/articles"))
                .logout(logout -> logout
                        .logoutSuccessUrl("/login")
                        .invalidateHttpSession(true))
                .csrf(AbstractHttpConfigurer::disable) // csrf 비활성화. 테스트시에 번거러우니까능
                .build();
    }

    // @Bean
    // public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    //     return http
    //         .authorizeRequests(auth -> auth
    //             .requestMatchers("/login", "/signup", "/user", "/articles").permitAll() // 로그인, 회원가입, /articles 등 공개
    //             .anyRequest().authenticated() // 그 외 요청은 인증 필요
    //         )
    //         .formLogin(formLogin -> formLogin
    //             .loginPage("/login")
    //             .defaultSuccessUrl("/articles") // 로그인 후 /articles로 리디렉션
    //         )
    //         .logout(logout -> logout
    //             .logoutSuccessUrl("/articles") // 로그아웃 후 /articles로 리디렉션
    //             .invalidateHttpSession(true)
    //         )
    //         .csrf(AbstractHttpConfigurer::disable) // CSRF 비활성화
    //         .build();
    // }

    @Bean
    public AuthenticationManager authenticationManager(HttpSecurity http, BCryptPasswordEncoder bCryptPasswordEncoder,
                                                       UserDetailService userDetailService) throws Exception{
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
        authProvider.setUserDetailsService(userService);
        authProvider.setPasswordEncoder(bCryptPasswordEncoder);
        return new ProviderManager(authProvider);
    }

    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder(){
        return new BCryptPasswordEncoder(); //로그인, 회원 가입 시 비밀번호를 암호화
    }
}
