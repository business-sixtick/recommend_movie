package com.recommend.movie;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication
@EntityScan(basePackages = "com.recommend.movie.springbootdeveloper.domain")  // 엔티티 패키지 명시
@EnableJpaRepositories // JPA 레포지토리 활성화
public class MovieApplication {

	public static void main(String[] args) {
		SpringApplication.run(MovieApplication.class, args);
		System.out.println("=======================================SVT FOREVER");
	}

}
