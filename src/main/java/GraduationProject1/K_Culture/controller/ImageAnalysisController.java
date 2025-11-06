package GraduationProject1.K_Culture.controller;

import GraduationProject1.K_Culture.dto.RequestImageDTO;
import GraduationProject1.K_Culture.service.FlaskService2;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Base64;
import java.util.Map;

//프론트엔드로부터 MultipartFile과 year를 받고, Base64로 변환하여 서비스로 전달
@RestController
@RequiredArgsConstructor
public class ImageAnalysisController {
    private final FlaskService2 flaskService;

    @PostMapping("/upload")
    public ResponseEntity<?> uploadImageAndYear(
            @RequestPart("image") MultipartFile imageFile,
            @RequestPart("year") String year) throws IOException {
        if (imageFile.isEmpty() || year == null || year.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("message", "파일과 연도는 필수입니다."));
        }

        //1.이미지 데이터를 Base64 문자열로 인코딩
        String base64Image = Base64.getEncoder().encodeToString(imageFile.getBytes());
        System.out.println("✅ Spring: 받은 연도: " + year);
        System.out.println("✅ Spring: Base64 문자열 길이: " + base64Image.length());


        //2.Flask로 보낼 DTO 객체 생성
        RequestImageDTO dto = new RequestImageDTO();
        dto.setBase64Image(base64Image);
        dto.setYear(year);
        dto.setFileName(imageFile.getOriginalFilename());

        try {
            //3.Flask 서비스 호출 및 응답 받기
            //FlaskService는 Map<String,String>형태의 응답을 반환한다고 가정
            Map<String, String> flaskResponse = flaskService.sendImageToFlask(dto);

            //4.Flask 응답을 그대로 클라이언트에게 JSON형태로 전달
            return ResponseEntity.ok(flaskResponse);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("message", "Flask 통신 중 오류발생: " + e.getMessage()));
        }
    }
}
