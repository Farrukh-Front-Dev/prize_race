---
inclusion: always
---

# PrizeRace — Senior Developer Qoidalari

## Loyiha haqida
- **Stack:** FastAPI + PostgreSQL + Tarantool (backend), React 18 + TypeScript + Vite + TailwindCSS + Zustand + TanStack Query (frontend)
- **Auth:** `X-Telegram-Init-Data` header, HMAC-SHA256 validatsiya
- **User ID:** Har doim `request.state.telegram_id` dan ol — query param yoki body'dan HECH QACHON olma
- **PRD fayl:** `/home/farrukh/kwork/price_race/PrizeRace_PRD_Senior_UZ.md`

---

## Kod yozishdan OLDIN majburiy qadamlar

1. **Tegishli faylni o'qi** — taxmin qilma, avval o'qi
2. **Mavjud patternni tushun** — loyihada qanday yozilgan bo'lsa, shunday yoz
3. **Faqat so'ralgan narsani yoz** — qo'shimcha feature, "yaxshilab qo'yaman" deb o'zgartirish YO'Q

---

## Xavfsizlik qoidalari (buzilmaydi)

```
❌ async def join_event(event_id: int, user_id: int, ...)   # user_id tashqaridan kelmoqda
✅ async def join_event(event_id: int, request: Request, ...) # request.state.telegram_id
```

- `organizer_id == user_id` tekshiruvi — tashkilotchi o'z eventiga kira olmaydi
- Account yoshi < 30 kun → 403
- Duplicate join → `IntegrityError` → 400 "already joined"
- Race condition → Tarantool lock → 429

---

## Tarantool qoidalari

- Leaderboard faqat Tarantool'dan o'qiladi (tezlik: O(log N))
- PostgreSQL'ga yozish — asinxron navbat orqali (serverga zo'riqish berma)
- Lock key formati: `lock:{telegram_id}:{path}:{method}` — TTL 3 soniya

---

## Frontend qoidalari

- Barcha asosiy tugmalar (`join`, `verify`) — so'rov ketayotganda `disabled` + spinner
- 400 xato → tugma matni "Siz allaqachon qatnashyapsiz"ga o'zgarsin
- 429 xato → Toast: "Iltimos kuting, so'rovingiz ishlanmoqda"
- 10 000+ ishtirokchi bo'lsa → `react-window` virtualizatsiya
- Axios Interceptors — global xato tutish

---

## Kod sifati standartlari

**Python:**
- `async/await` — hamma joyda
- `try/except IntegrityError` — duplicate himoya
- Type hints — barcha funksiyalarda
- `.dict(exclude_unset=True)` — partial update uchun

**TypeScript:**
- `unknown` ishlatilsin, `any` YO'Q
- `const` — `let` o'rniga
- Har bir API chaqiruvda loading state boshqarilsin

---

## Sprint holat mashinkasi (o'zgartirma)

```
DRAFT → PENDING_PAYMENT → ACTIVE → FINISHED
```
- `ACTIVE` bo'lmagan eventga join → 400
- `DRAFT` bo'lmagan eventni update → 400
- `FINISHED` eventni hech narsa o'zgartira olmaydi

---

## Tez-tez uchraydigan xatolar (qilma)

| Xato | To'g'ri yo'l |
|------|-------------|
| `user_id` query param | `request.state.telegram_id` |
| Tarantool ishlamasa skip | Log + fallback, lekin lock logikasi ishlashi shart |
| Frontend'da `any` type | `unknown` yoki aniq type |
| N+1 query | `user_ids` batch fetch, keyin `user_map` |
| Har safar PostgreSQL'dan leaderboard | Tarantool'dan o'qi |
