package GraduationProject1.K_Culture.service;

import GraduationProject1.K_Culture.dto.RequestImageDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class FlaskService2 {

    private final RestTemplate restTemplate;

    private final String FLASK_API_URL = "http://localhost:8082/analyze_image";

    public Map<String, String> sendImageToFlask(RequestImageDTO dto){
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        //Flask로 보낼 DTO를 HttpEntity에 담습니다.
        HttpEntity<RequestImageDTO> entity = new HttpEntity<>(dto, headers);

        //Flask API 호출(응답은 Map<String, String>형태로 받음)
        ResponseEntity<Map<String, String>> response = restTemplate.exchange(FLASK_API_URL,
                HttpMethod.POST,
                entity,
                new ParameterizedTypeReference<Map<String, String>>() {}
        );

        if(response.getStatusCode().is2xxSuccessful() && response.getBody() != null){
            return response.getBody();
        }else {
            throw new RuntimeException("Flask 이미지 분석 API 호출 실패. 상태 코드:"+response.getStatusCode());
        }
    }

}
