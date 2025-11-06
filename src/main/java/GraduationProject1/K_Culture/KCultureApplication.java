package GraduationProject1.K_Culture;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class KCultureApplication {
	public static void main(String[] args) {
		SpringApplication.run(KCultureApplication.class, args);
	}

	// ✅ RestTemplate을 Bean으로 등록하는 메서드
	@Bean
	public RestTemplate restTemplate() {
		return new RestTemplate();
	}
}
