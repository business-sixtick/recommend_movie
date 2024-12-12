package com.recommend.movie;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@EnableJpaAuditing
// @EntityScan(basePackages = "com.recommend.movie.springbootdeveloper.domain")  // 엔티티 패키지 명시
@EnableJpaRepositories // JPA 레포지토리 활성화
@SpringBootApplication(exclude = {
    org.springframework.boot.autoconfigure.h2.H2ConsoleAutoConfiguration.class,
    org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration.class
})
public class MovieApplication {
	public static void main(String[] args) {
		SpringApplication.run(MovieApplication.class, args);
		System.out.println("==================================================SVT FOREVER");
	}

}

// movie\src\main\java\com\recommend\movie\MovieApplication.java