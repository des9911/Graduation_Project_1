package GraduationProject1.K_Culture.controller;

import GraduationProject1.K_Culture.dto.RequestSendtoFlaskDTO;
import GraduationProject1.K_Culture.service.FlaskService;
import com.fasterxml.jackson.core.JsonProcessingException;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class FlaskContoller {

    private final FlaskService flaskService;

    @PostMapping("/flask")
    public String sendToFlask(@RequestBody RequestSendtoFlaskDTO dto) throws JsonProcessingException {
        return flaskService.sendToFlask(dto);
    }
}
