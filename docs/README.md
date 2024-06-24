# 목표

토지 정보를 보여주는 rest api 제공

### 최소요구사항

- [] 회원가입을 할 수 있다.
  - [] 회원가입에 대한 엔드포인트를 적어주세요. ()
  - [] 입력 데이터에 대한 유효성 검사를 한다.
  - [] 성공 시 메시지를 반환한다.
  - [] (필요한 경우) 성공 시 토큰 등을 반환해 바로 로그인
  - [] 실패 시 메시지를 반환한다.
- [] 로그인을 할 수 있다.
  - [] 로그인에 대한 엔드포인트를 적어주세요. ()
  - [] 로그아웃에 대한 엔드포인트를 적어주세요. ()
  - [] 성공 시 토큰, id 등을 반환한다.
  - [] 실패 시 메시지를 반환한다.
- [] 토지 DB를 만든다.
  - [] 토지 model을 만든다.
- [] 토지 리스트를 제공할 수 있다.
  - [] 토지 리스트에 대한 엔드포인트를 적어주세요. ()
  - [] 페이지네이션을 할 수 있다.
  - [] 필터링을 지원한다.
  - [] 성공 시 json 데이터를 응답한다.
- [] 토지 상세를 제공할 수 있다.
  - [] 토지 상세에 대한 엔드포인트를 적어주세요. ()
  - [] 성공 시 json 데이터를 응답한다.
  - [] 실패 시 메시지를 반환한다.

- (향후) 회원에 따른 미들웨어, 모델링 등