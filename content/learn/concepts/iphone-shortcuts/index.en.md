+++
title = "iPhone 단축어 (iPhone Shortcuts)"
date = 2026-06-16
draft = false
description = "iPhone 단축어 (iPhone Shortcuts) -  learners"
categories = []
tags = ["iphone", "shortcuts", "automation", "ios", "productivity"]
level = ""
type = ""
wikilink = "obsidian://open?vault=workspace&file=wiki/concepts/lifestyle/iPhone_Shortcuts.md"
+++
# iPhone 단축어 (iPhone Shortcuts)

## 핵심 정의

**iPhone 단축어(Shortcuts)** 는 iOS에 기본 내장된 **자동화 도구**로, 여러 작업을 **하나의 워크플로우로 묶어** 버튼 한 번 또는 자동 트리거로 실행할 수 있게 합니다. 2018년 Workflow 앱 인수 후 iOS 12부터 기본 통합되었으며, **코딩 없이도 강력한 자동화**가 가능합니다.

## 핵심 기능

### 1. 단축어 (Shortcut)
- **수동 실행:** 버튼, Siri, 홈 화면 위젯, 잠금 화면
- **입력:** 텍스트, 이미지, URL, 위치 등
- **출력:** 앱 실행, 알림, TTS(Text-to-Speech), 텍스트 표시

### 2. 자동화 (Automation)
- **시간 기반:** 매일/매주/매월 특정 시각
- **위치 기반:** 집, 사무실 등 특정 장소 도착/출발
- **앱 기반:** 특정 앱 열기/닫기
- **기기 기반:** 충전 시작/종료, 블루투스 연결 등

### 3. 액션 (Action)
- 300+ 내장 액션
- **앱 통합:** 사진, 음악, 캘린더, 메시지, 전화 등
- **시스템:** 설정 변경, 알림, 진동
- **외부 API:** HTTP 요청, JSON 파싱

## 실전 활용 사례

### 1. 모닝 루틴 (Morning Routine)
```
[트리거: 아침 6:00]
- 알람 끄기
- TTS: "좋은 아침입니다, 현재 기온은 25도, 맑음"
- 오늘 일정 표시
- 뉴스 앱 자동 열기
```

### 2. 운전 모드 (Driving Mode)
```
[트리거: 차량 블루투스 연결]
- T맵 자동 실행
- 볼륨 자동 조절 (70%)
- 운전방해금지 켜기
- 음악 플레이리스트 시작
```

### 3. 앱테크 출석 (App-Tech Attendance)
```
[트리거: 매일 오전 9:00]
- 알림 표시: "앱테크 출석 시간!"
- 해당 앱 딥링크 열기
- 5분 후 다음 앱 알림
```

### 4. 다중 알람 (Multiple Alarms)
```
[트리거: 수동 실행]
- 목록: [06:00, 06:30, 07:00, 07:30]
- "Repeat with Each" → "Create Alarm"
- 4개 알람 한 번에 생성
```

### 5. 사진 정리
```
[트리거: 수동 실행]
- "Find Photos" (오늘 찍은 사진)
- "Resize Image" (1024x1024)
- "Save to Album" (자동 저장)
```

## 시작 가이드

### Step 1: 갤러리 탐색
- 단축어 앱 > 갤러리 탭
- 인기/추천 단축어 5-10개 설치
- 직접 사용해보기

### Step 2: 간단한 단축어 만들기
1. 단축어 앱 > + 버튼
2. 액션 추가 (예: "Get Current Weather")
3. 다음 액션 추가 (예: "Speak Text")
4. 테스트 실행
5. 홈 화면에 추가 (옵션)

### Step 3: 자동화 설정
1. 자동화 탭 > + 버튼
2. 트리거 선택 (시간/위치/앱)
3. 새 단축어 만들기 또는 기존 단축어 선택
4. 활성화

### Step 4: 고급 활용
- 변수 사용 (Set Variable)
- 조건문 (If)
- 반복 (Repeat with Each)
- API 호출 (Get Contents of URL)

## 장단점

### 장점
- **무료:** iOS 기본 내장
- **코딩 불필요:** 블록 기반
- **강력한 통합:** iOS 시스템 + Apple 앱
- **공유 가능:** 가족/지인 공유
- **갤러리:** 검증된 단축어 활용

### 단점
- **iOS 한정:** Android 미지원
- **제한적 API:** 일부 앱은 통합 안 됨
- **복잡한 로직:** 고급 워크플로우는 어려움
- **배터리:** 위치 기반 자동화는 소모 ↑
- **디버깅 어려움:** 어디서 실패했는지 파악 어려움

## 고급 활용 팁

### 팁 1: 변수 활용
```
[Get Current Date] → [Set Variable: today]
[Format Date] → [Set Variable: today_str]
[Display Notification: today_str]
```

### 팁 2: 조건문
```
[If: 시간 < 12:00]
  [Speak Text: "좋은 아침"]
[Otherwise]
  [Speak Text: "좋은 오후"]
```

### 팁 3: API 호출
```
[Get Contents of URL]
  URL: "https://api.weather.com/..."
  Method: GET
[Get Dictionary Value]
[Show Result]
```

### 팁 4: 다른 앱 딥링크
```
[Open URL: "tmap://route?goalname=..."]
[Open URL: "kakaotalk://..."]
[Open URL: "naversearchapp://..."]
```

## 주의사항

### 권한 관리
- **위치:** 자동화 트리거에 필요
- **사진:** 갤러리 작업 시
- **캘린더:** 일정 접근
- **알림:** 알림 발송
- **연락처:** 메시지 발송

### 개인정보 보호
- 외부 API 호출 시 데이터 전송 주의
- 공유 단축어는 신중 검토
- 위치 데이터는 신뢰할 수 있는 앱에만 허용

### 배터리 최적화
- 위치 자동화는 필요한 경우만
- 트리거 조건 명확히
- 사용하지 않는 자동화 비활성화

## 한국 사용자 팁

### 카카오/네이버 통합
- 카카오톡 메시지 자동 발송
- 네이버 뉴스/지도 자동 실행
- 카카오페이 알림 처리

### 자주 사용 단축어
- 지하철 도착 알림
- 배달 음식 추적
- 한국 주식 차트 확인
- 한글 입력 단축키

### 한국 한정 단축어
- 네이버 파파고 번역
- 카카오 T 대리 운전자 호출
- 배달의민족 쿠폰 확인

## 관련 개념

- [[Personal_Automation]] - 개인 자동화
- [[Life_Hack_Methodology]] - 라이프 해킹
- [[Productivity_Tools]] - 생산성 도구
- [[Morning_Routine_Automation]] - 모닝 루틴
- App_Tech_Automation - 앱테크
- [[2026-06-16_iPhone_Shortcuts|블로그: iPhone 단축어]]

## 추가 학습

- Apple 공식 Shortcuts User Guide
- MacStories Shortcuts Archive
- RoutineHub.co (커뮤니티)
- Reddit: r/shortcuts
- YouTube: "Shortcuts Saturday" 시리즈