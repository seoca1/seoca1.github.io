+++
title = "스테이블 코인 기초 (Stablecoin Fundamentals)"
date = 2026-06-16
draft = false
description = "스테이블 코인 기초 (Stablecoin Fundamentals) -  learners"
categories = []
tags = ["stablecoin", "cryptocurrency", "usdt", "usdc", "dai", "defi"]
level = ""
type = ""
wikilink = "obsidian://open?vault=workspace&file=wiki/concepts/finance/Stablecoin_Fundamentals.md"
+++
# 스테이블 코인 기초 (Stablecoin Fundamentals)

## 🎯 핵심 정의

**스테이블 코인(Stablecoin)** 은 **법정화폐(주로 USD)에 페그(peg)** 된 암호화폐로, **가격 안정성**을 목표로 합니다. 변동성이 큰 일반 암호화폐(BTC, ETH)와 달리, 1 스테이블코인 ≈ 1 USD의 가치를 유지하도록 설계되었습니다. **암호화폐 거래의 브릿지**이자 **온체인 달러**로 기능합니다.

## 📝 주요 종류

### 1. 법정화폐 담보형 (Fiat-Collateralized)
**실제 USD/USD 등가물을 보유**하고 그에 상응하는 코인 발행

| 코인 | 발행사 | 시가총액(2025) | 특징 |
|:---|:---|:---:|:---|
| **USDT (Tether)** | Tether Limited | $120B+ | 가장 큰 거래량, 뉴욕 vs 홍콩 |
| **USDC (USDC)** | Circle | $40B+ | 규제가 더 친화적, 미국 중심 |
| **TUSD (TrueUSD)** | TrueCoin | $1B+ | 감사 강조 |
| **BUSD (Binance USD)** | 바이낸스/Paxos | 종료 | 2023년 단계적 종료 |
| **PYUSD (PayPal USD)** | PayPal/Paxos | $1B+ | 페이팔 발행 |

### 2. 암호화폐 담보형 (Crypto-Collateralized)
**ETH 등 다른 암호화폐를 담보**로 사용, **초과 담보** (150%+)

- **DAI (MakerDAO)**
- 발행 시 ETH 등 담보
- 150-200% 담보율로 안전성 확보

### 3. 알고리즘형 (Algorithmic)
**알고리즘으로 공급 조절**, 담보 없음 → **위험도 매우 높음**

- **Terra UST (2022 붕괴):** 대실패 사례
- 알고리즘 안정성은 이론과 현실 괴리 큼
- 현재는 거의 사용되지 않음

## 🎯 사용 목적

### 1. 거래 브릿지
- BTC ↔ USDT (급격한 가격 변동 회피)
- 거래소 간 송금 (빠르고 저렴)
- "암호화폐 시장의 달러"

### 2. 송금 (Remittance)
- **해외 송금 비용:** SWIFT 대비 80%+ 절감
- 예: 미국 → 필리핀 송금
  - 전통: 7-10% 수수료, 3-5일
  - USDT: 1% 미만 수수료, 10분

### 3. 결제 (Payment)
- **Visa/Mastercard 파트너십**
- **PayPal (2020)**
- **Stripe (재도입)**
- 인터넷 쇼핑, 인보이스 결제

### 4. DeFi (탈중앙화 금융)
- Lending 프로토콜 (Aave, Compound)
- Yield Farming
- 스마트 계약의 "달러"

### 5. 국가/기업 보유
- 옐리프, 지니, 직맥 등 한국 결제 서비스
- 일부 국가의 법정화폐 대안 (예: 일부 국가)

## ⚖️ 장단점

### 장점
- ✅ **가격 안정성** (1 USD ≈ 1 USDC)
- ✅ **빠른 거래** (분 단위)
- ✅ **낮은 수수료** (특히 해외 송금)
- ✅ **24/7 운영** (은행 영업시간 무관)
- ✅ **글로벌 접근성** (인터넷만 있으면)
- ✅ **프로그래머블** (스마트 계약 통합)

### 단점 / 리스크
- ❌ **중앙화:** Tether, Circle이 발행량 통제
- ❌ **규제 리스크:** 미국/한국 정부 규제
- ❌ **감사 투명성:** Tether의 USD 보유 감사 논란
- ❌ **은행 접근:** 발행사가 은행 계좌 유지 어려움
- ❌ **상환 리스크:** 모든 코인을 동시에 상환할 수 있는가?
- ❌ **거래소 리스크:** FTX 붕괴 시 USDC 가치 영향

## 📊 2025년 시장 상황

### 시가총액 분포
- 전체 스테이블코인 시장: ~$200B
- USDT: ~60%
- USDC: ~20%
- 신규 진입: PYUSD, FDUSD

### 주요 트렌드
1. **규제 강화:** 미국 GENIUS Act, EU MiCA
2. **기관 채택:** BlackRock BUIDL, Franklin Templeton BENJI
3. **은행권 진입:** JPMorgan JPM Coin, Citi
4. **CBDC와의 경쟁:** 각국 디지털 화폐

## 🇰🇷 한국 상황

### 국내 거래소
- **업비트, 빗썸, 코인원:** USDT 거래 지원
- **원화 직거래 vs USDT 거래:** 한국은 원화 직접 거래 가능

### 규제
- **특금법 (특정 금융정보법):** 2022년 시행
- **가상자산 이용자 보호법:** 2024년 시행
- **스테이블코인 발행:** 한국 발행사 없음 (USDT/USDC만 거래)

### 활용 사례
- **해외 송금:** 코빗, 한패스 등
- **암호화폐 마진 거래:** USDT/USDC 담보
- **단순 보유:** 현금 대안 (그러나 리스크 인지)

## ⚠️ 리스크 관리

### 보관 방법별 리스크
| 보관 방법 | 리스크 | 권장도 |
|:---|:---|:---:|
| **거래소 보관** | 해킹, 파산 | ❌ (일부만) |
| **하드웨어 지갑 (Ledger, Trezor)** | 분실, 피싱 | ✅ |
| **소프트웨어 지갑 (MetaMask)** | 해킹, 피싱 | ⚠️ |
| **콜드 스토리지 (종이)** | 분실, 손상 | ✅ |

### 다각화 전략
- ✅ 단일 발행사 의존 ❌
- ✅ USDT + USDC 혼합
- ✅ 정기적인 출금/검증

## 🔗 관련 개념

- [[Michael_Saylor_Bitcoin_Strategy]] - 스테이블코인의 등장 배경
- [[Fiat_Currency_Inflation]] - 법정화폐 대안
- [[Bitcoin_Investment_Risks]] - 암호화폐 리스크
- [[Asset_Allocation_Principles]] - 현금 자산의 새로운 형태
- [[Multi_Currency_Diversification]] - 다통화 분산
- DeFi_Overview - 탈중앙화 금융

## 📚 추가 학습

- **Circle 공식 문서** (USDC)
- **Tether 투명성 보고서** (USDT)
- **"Why Stablecoins Matter"** (a16z)
- **"Stablecoins and the Future of Money"** (Citi GPS)
- **MiCA (EU) / GENIUS Act (US)** 규제 문서