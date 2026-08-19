# 행정사사무소 업무 플로우 이식 패키지 (haengjeongsa-office-flow)

유영행정사사무소가 실제 운영 중인 사건 접수·수임 확정·채번·문서 발급·폴더 체계·Notion
사건관리 플로우를 다른 행정사사무소에 그대로 이식하는 패키지입니다. 무상 공유하며 재판매는
금지합니다.

## 구성

스킬 다섯 개와 템플릿으로 이루어져 있습니다.

1. office-setup-wizard — 설치 마법사. 설치 후 가장 먼저 "사무소 셋업"이라고 말해 실행합니다.
   사무소 정보를 입력받아 설정 파일, PC 폴더 구조, 채번부·등록대장, Notion DB 3종, 생성기
   스크립트를 만들고 테스트 발급으로 검증합니다.
2. office-case-init — 상담 접수, 수임 확정, 사건 개시.
3. case-folder-organizer — 사건 폴더 종류별 정리.
4. hwpx-form-fill — 법령 별지·관공서 hwpx 서식 값 채우기.
5. hwp-render-convert — hwp→hwpx 변환과 PDF·PNG 검수 렌더.

## 설치 전 준비물

자세한 목록은 설치 마법사가 안내합니다. 요지는 사무소 식별정보(자격번호·업무신고번호·사업자
등록번호 등), 입금 계좌, Notion 계정, 구글 계정, 한컴 한글과 Python 3.10 이상이 설치된
Windows PC, Claude 데스크탑 앱입니다. 유영행정사사무소의 계정이나 API는 사용되지 않으며
모든 계정은 설치받는 사무소가 자체 준비합니다.

## 설치 방법

Claude 데스크탑 앱(Cowork)에서 이 플러그인 파일(.plugin)을 대화에 끌어다 놓고 설치를 승인한
뒤, 새 대화에서 "사무소 셋업"이라고 입력하면 설치 마법사가 시작됩니다.

Claude Code 사용자는 다음 두 명령으로 설치합니다.

    /plugin marketplace add kangship/office-flow
    /plugin install haengjeongsa-office-flow@youyoung-marketplace

## 문의

유영행정사사무소 · kang@youyoungpro.com · blog.youyoungpro.com
