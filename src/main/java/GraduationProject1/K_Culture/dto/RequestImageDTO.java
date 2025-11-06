package GraduationProject1.K_Culture.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class RequestImageDTO {
    //Flask로 전달할 필드
    private String base64Image; //Base64로 인코딩된 이미지 문자열
    private String year;    //연도 문자열
    private String fileName;    //파일이름(참고용)
}
