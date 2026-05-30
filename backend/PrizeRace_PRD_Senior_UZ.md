# Texnik Vazifa (PRD) — PrizeRace MVP Platformasi (v1.5)

## 1. Kirish va Loyihaning Biznes-Logikasi
**PrizeRace** — bu Telegram Mini App (TMA) ekotizimida geymifikatsiya qilingan sprintlar (yutuqli o'yinlar) o'tkazish uchun mo'ljallangan Web3 platformasi. Tashkilotchilar TON kriptovalyutasida mukofot jamg'armasini yaratadilar, foydalanuvchilar esa ijtimoiy va ichki topshiriqlarni bajarib, XP (ochko) yig'adilar va jonli reytingda (Leaderboard) Top-N g'oliblar qatoriga kirish uchun bellashadilar. Mukofotlarni tarqatish blokcheyndagi desentralizatsiyalangan smart-kontrakt orqali to'liq avtomatlashtirilgan.

### Biznes maqsad:
Inson omilini (firbgarlik, to'lovlarni kechiktirish) butunlay yo'q qilish, topshiriqlar tekshiruvini avtomatlashtirish va foydalanuvchilarga ochkolar lahzalarda hisoblanadigan shaffof reyting tizimini taqdim etish.

---

## 2. Global Ish Oqimi (Sprint Hayotiy Sikli / Flow)

```
 [ DRAFT ] ──────────► [ PENDING_PAYMENT ] ──────────► [ ACTIVE ] ──────────► [ FINISHED ]
     │                         │                          │                        │
 Tashkilotchi             Konfiguratsiya            Depozit tasdiqlandi.      Muhlati tugadi.
 sozlamalari.             muzlatildi, TON           Sprint hamma uchun        Rust Orakul
 To'liq tahrirlash        depoziti kutilmoqda.       faol. O'zgartirish       g'oliblarga avtomat
 imkoniyati bor.                                     MUTLAQ TAQIQLANADI.       TON tarqatadi.
```

1. **Yaratish:** Tashkilotchi interfeys orqali sprintni sozlaydi (Top-N g'oliblar soni, topshiriqlar ro'yxati, yakunlanish vaqti, mukofot summasi). Sprint `DRAFT` statusida yaratiladi.
2. **Parametrlarni muzlatish:** Tashkilotchi sozlashni yakunlaydi, sprint `PENDING_PAYMENT` holatiga o'tadi. Backend parametrlarni o'zgartirishni bloklaydi.
3. **Depozit va Aktivlashtirish:** Tashkilotchi hamyonini ulaydi va smart-kontraktga TON yuboradi. Blokcheyn tranzaksiyasi backend tomonidan validatsiya qilingach, status `ACTIVE`ga o'zgaradi va sprint barcha foydalanuvchilarga ko'rinadi.
4. **Ishtirok etish:** Ishtirokchilar topshiriqlarni bajarishadi. Reyting (Leaderboard) real vaqt rejimida qayta hisoblab boriladi.
5. **Final va Yakuniy Taqsimot:** Muddat tugashi bilan backend sprintni `FINISHED` statusiga o'tkazadi. Avtonom Rust-orakuli Tarantool'dan Top-N g'oliblarning yakuniy ro'yxatini oladi va blokcheyndagi smart-kontraktning `Distribute` metodini chaqirib, mablag'larni g'oliblar ko'shlyoklariga avtomat o'tkazadi.

---

## 3. BACKEND DEVELOPER uchun vazifalar taqsimoti

### Arxitekturaviy Stack:
* **Til / Freymvork:** Python 3.11+ / FastAPI (Asinxron rejim).
* **Ma'lumotlar bazasi:** PostgreSQL 15 (Doimiy relatsiyaviy ma'lumotlar) + Tarantool DB (In-memory reyting, kesh, sepslar va blokirovka semaforlari).
* **Avtorizatsiya:** Har bir so'rovda HMAC-SHA256 kaliti yordamida `X-Telegram-Init-Data` sarlavhasini sevsiz (Stateless) validatsiya qilish.

### Konkret Texnik Vazifalar:

#### Vazifa B-1: Ma'lumotlar Bazasi Sxemasi va Idempotentlik (Eng muhim vazifa)
* `users`, `events` (sprintlar), `tasks`, `participants` (ishtirokchilar) va `user_task_completions` jadvallarini loyihalash.
* **Bot ichida dublikatdan himoya ("Foydalanuvchi botda"):** PostgreSQL'dagi `users` jadvalining `telegram_id` maydoniga `UNIQUE` indeksi o'rnatilsin. Foydalanuvchi botni qayta `/start` qilganda yoki yangi referal link bilan kirganda bazada yangi qator ochilmasligi uchun `Upsert` (Insert on Conflict Update) logikasi yozilsin. Referal ochkolar faqat birinchi marta kirgandagina hisoblansin.
* **Sprint ichida dublikatdan himoya ("Foydalanuvchi sprintda"):** `participants` jadvaliga `UNIQUE (user_id, event_id)` kompozit kaliti o'rnatilsin. Agar foydalanuvchi bir marta qo'shilgan bo'lsa, baza parallel kelgan ikkinchi so'rovni jismonan rad etsin (`UniqueViolationError`).
* **Poyga Holati (Race Condition) Blokirovkasi:** Tarantool DB bazasida FastAPI Middleware (Idempotency Lock) yozilsin. Foydalanuvchi `/api/events/:id/join` endpointiga so'rov yuborganda, atomar tarzda 3 soniyalik TTL bilan `lock:user_id:event_id` kaliti yaratilsin. Shu millisekund ichida kelgan barcha parallel takroriy so'rovlar bazaga o'tmasdan, `429 Too Many Requests` xatoligi bilan qaytarilsin.

#### Vazifa B-2: Yuqori Yuklamali Reyting Tizimi (Tarantool Leaderboard)
* Tarantool DB integratsiyasini qilish. Sprintlar reytingini saqlash uchun `TREE` indeksli (XP bo'yicha saralangan) speys yaratilsin.
* XP qo'shish logikasi: foydalanuvchi topshiriqni muvaffaqiyatli bajarganda backend reytingni Tarantool ichida lahzalarda yangilaydi (operatsiya tezligi $O(\log N)$), PostgreSQL bazasiga esa ma'lumotlar serverni zo'riqtirmaslik uchun asinxron navbat (Queue) orqali yozib boriladi.

#### Vazifa B-3: REST API Endpointlarini ishlab chiqish
* `GET /api/me` — joriy foydalanuvchi profili, statusi va ulangan hamyonini tekshirish.
* `GET /api/events` — faol va tugagan sprintlar ro'yxatini qaytarish.
* `POST /api/events/:id/join` — sprintda ro'yxatdan o'tish (Idempotency Lock filtridan o'tkazgan holda).
* `POST /api/tasks/:id/verify` — topshiriqni tekshirish (Telegram Bot API orqali `getChatMember` metodini chaqirib, homiy kanalga a'zolikni tekshirish).

---

## 4. FRONTEND DEVELOPER uchun vazifalar taqsimoti

### Arxitekturaviy Stack:
* **Kutubxonalar / Sborshik:** React 18 / TypeScript / Vite.
* **Stillar:** Tailwind CSS (Telegram Mini App WebView uchun maxsus moslashuvchan Mobile-first interfeys).
* **Shtat boshqaruvi (State Manager):** Ma'lumotlarni keshdan o'chirish va sinxronizatsiya qilish uchun Axios + TanStack Query (React Query).
* **Web3 Integratsiya:** TON tarmog'ida avtorizatsiya va tranzaksiyalarni amalga oshirish uchun `@tonconnect/ui-react` SDK.

### Konkret Texnik Vazifalar:

#### Vazifa F-1: Mobile-first Interfeys va UX Optimizatsiyasi
* Asosiy ekran maketi: mavjud sprintlar ro'yxati, ularning statuslari (Active, Finished) va tugash muddatiga qolgan vaqt taymeri (Countdown progress-bar).
* Reyting Ekrani: Top-N g'oliblarni chiroyli ko'rsatish. Agar sprintda 10 000 dan ortiq ishtirokchi bo'lsa, kuchsiz telefonlarda qotishlar (lag) bo'lmasligi uchun ro'yxatni virtualizatsiya qilish mexanizmi (`react-window`) joriy etilsin.
* Tarmoq xatoliklari va yuklanish holatlarini (Skeleton loaders) vizual render qilish.

#### Vazifa F-2: TON Connect Integratsiyasi va Klik-Flud Himoyasi
* Ilova ildiziga (root) `<TonConnectUIProvider>` ulansin.
* Hamyonni ulash logikasi: hamyon manzili faqat kriptografik imzo (Proof alignment) tekshiruvidan o'tgandan keyingina backenddagi `POST /api/me/wallet` endpointiga yuborilsin.
* **Double-click (Ikki marta bosish) himoyasi:** Interfeys tomondan serverga ketma-ket so'rovlar oqimi yuborilishining oldini olish uchun barcha asosiy tugmalarda (ayniqsa "Qatnashish", "Tekshirish") so'rov ketayotgan vaqtda tugmani dasturiy bloklash (`disabled` holat + spinner animatsiyasi) mexanizmi joriy etilsin.

#### Vazifa F-3: Backenddan keladigan Idempotentlik xatolarini qayta ishlash
* Global xatoliklarni tutib qolish tizimi (Axios Interceptors) sozlansin.
* Agar backend `400 Bad Request` (Foydalanuvchi sprintda allaqachon bor) xatosini qaytarsa, interfeys darhol tugma matnini "Siz allaqachon qatnashyapsiz" holatiga o'tkazishi va modal oynani yopishi kerak.
* Agar backend `429 Too Many Requests` (Tarantool'dagi Idempotency Lock ishladi) xatosini qaytarsa, ekranda chiroyli Toast-bildirishnoma orqali "Iltimos kuting, so'rovingiz ishlanmoqda" matni chiqarilsin.

---

## 5. Anti-Frod (Firbgarlikka qarshi) Matritsasi (Birgalikdagi mas'uliyat hududi)

| Qoida / Trigger | Biznes Logika va Ta'rif | Amalga oshirilishi (Backend + Frontend) |
| :--- | :--- | :--- |
| **Akkaunt yoshi filtri** | Botlar va soxta fermalardan himoya. Ochilganiga 30 kundan kam bo'lgan Telegram akkauntlari sprintga kiritilmaydi. | **Backend:** `initData` ichidagi vaqt belgisini hisoblab, 403 xatosi beradi. <br>**Frontend:** Akkaunt bloklangani haqida ogohlantirish ekranini ko'rsatadi. |
| **Homiylik obunasi nazorati**| Foydalanuvchi majburiy kanallardan chiqib ketsa, to'plagan barcha XP ochkolari avtomat nol qilinadi. | **Backend:** Kundalik asinxron Cron-vazifasi Telegram API orqali tekshirib, Tarantool va PostgreSQL'da XPni o'chiradi. |
| **Referal tizim limiti** | Bir sutkada bitta foydalanuvchi maksimal 20 ta referal taklif qila oladi. | **Backend:** Tarantool ichida `ref:daily:user_id` kaliti ostida kunlik counter hisoblab boriladi. |
| **Manfaatlar to'qnashuvi** | Sprint tashkilotchisi o'zi yaratgan musobaqada ishtirokchi bo'lib qatnasha olmaydi. | **Backend:** `/join` endpointida `organizer_id == user_id` tekshiruvi. <br>**Frontend:** Tashkilotchi uchun ishtirok etish tugmasini yashiradi. |

---

## 6. Rust Orakulida Chekka Holatlarni (Edge Cases) qayta ishlash algoritmi

Blokcheyn bilan ishlashda tranzaksiyalar xavfsizligini ta'minlash uchun Orakul algoritmiga alohida qoida kiritilgan:

1. **Kritik holat ("O'lik hamyonlar"):** Foydalanuvchi Tarantool reytingida Top-N ichiga kirib g'olib bo'lgan, lekin musobaqa tugash vaqtiga (deadline) qadar Mini App ichida o'zining TON hamyon manzilini profiliga biriktirmagan.
2. **Orakul yechim algoritmi:** Muddat tugashi bilan Rust-orakuli yakuniy g'oliblar ro'yxatini yuklaydi. Agar g'olib bo'lgan pozitsiyadagi foydalanuvchida `wallet_address` mavjud bo'lmasa, Orakul blokcheynga bo'sh manzil yubormaydi (bu smart-kontrakt tranzaksiyasini butunlay qulashiga olib keladi). 
   Orakul ushbu foydalanuvchini blokcheyn to'lovlar ro'yxatidan chiqarib tashlaydi, uning yutuq ulushi esa o'sha Top-N ro'yxatidagi **hamyoni ulangan qolgan barcha faol g'oliblar o'rtasida proporsional (teng ulushda) qayta taqsimlanadi**. Bu tizim pullarini kontrakt ichida bloklanib qolishidan 100% sug'urtalaydi.
