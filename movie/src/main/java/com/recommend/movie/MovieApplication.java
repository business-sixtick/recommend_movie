package com.recommend.movie;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@EnableJpaAuditing
@EntityScan(basePackages = "com.recommend.movie.springbootdeveloper.domain")  // 엔티티 패키지 명시
@EnableJpaRepositories(basePackages = "com.recommend.movie.springbootdeveloper.repository")
@SpringBootApplication(exclude = {
    org.springframework.boot.autoconfigure.h2.H2ConsoleAutoConfiguration.class,
    // org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration.class
	//스프링 부트가 db 연결을 설정할 대 사용하는 기본적인 클래스
	//이것을 제외하면 db와 연결할 수 없다
})
public class MovieApplication {
	public static void main(String[] args) {
		SpringApplication.run(MovieApplication.class, args);
		System.out.println("==================================================SVT FOREVER");
	}

}

// movie\src\main\java\com\recommend\movie\MovieApplication.java