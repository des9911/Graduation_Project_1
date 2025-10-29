package GraduationProject1.K_Culture.service;

import GraduationProject1.K_Culture.dto.RequestSendtoFlaskDTO;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
@RequiredArgsConstructor
public class FlaskService {

    //데이터를 json객체로 변환하기 위해서 사용
    private final ObjectMapper objectMapper;

    //@Transactional
    public String sendToFlask(RequestSendtoFlaskDTO dto) throws JsonProcessingException {
        RestTemplate restTemplate = new RestTemplate();

        //헤더를 json으로 설정
        HttpHeaders headers = new HttpHeaders();

        //파라미터로 들어온 dto를 json객체로 변환
        headers.setContentType(MediaType.APPLICATION_JSON);

        String param = objectMapper.writeValueAsString(dto);

        HttpEntity<String> entity = new HttpEntity<String>(param, headers);

        //실제 Flask 서버랑 연결하기 위한 URL
        String url = "http://127.0.0.1:8082/receive_string";

        //Flask서버로 데이터를 전송하고 받은 응답값을 return
        return restTemplate.postForObject(url, entity, String.class);
    }
}
