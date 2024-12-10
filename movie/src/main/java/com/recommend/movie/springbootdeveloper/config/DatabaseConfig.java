package com.recommend.movie.springbootdeveloper.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

@Configuration
public class DatabaseConfig {

    @Bean
    public DataSource dataSource() {
        HikariConfig hikariConfig = new HikariConfig();
        hikariConfig.setJdbcUrl("jdbc:mysql://192.168.0.26:3306/movie");
        hikariConfig.setUsername("ahncho");
        hikariConfig.setPassword("dkswh18");
        hikariConfig.setDriverClassName("com.mysql.cj.jdbc.Driver");
        return new HikariDataSource(hikariConfig);
    }
}
