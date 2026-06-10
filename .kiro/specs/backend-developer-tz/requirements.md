# Texnik Talablar Hujjati — PrizeRace Backend Developer TZ

## Kirish

Ushbu hujjat PrizeRace platformasining backend qismini to'liq ishga tushirish uchun texnik talablarni belgilaydi. PrizeRace — Telegram Mini App (TMA) ekotizimida geymifikatsiya qilingan sprintlar o'tkazish uchun mo'ljallangan Web3 platforma. Backend FastAPI + PostgreSQL + Tarantool stek asosida qurilgan bo'lib, loyiha ~55% tayyor holatda, ko'plab stub/TODO'lar mavjud.

Ushbu TZ barcha kritik xavfsizlik tuzatishlarini, PRD bo'yicha asosiy vazifalarni (B-1, B-2, B-3), anti-frod matritsasini, TON blockchain integratsiyasini, sprint holat mashinasini va background worker'larni qamrab oladi.

## Glossariy

- **Backend**: FastAPI (Python 3.11+) asosidagi asinxron REST API serveri
- **Tarantool**: In-memory ma'lumotlar bazasi — reyting, kesh, lock semaforlari uchun
- **PostgreSQL**: Doimiy relatsiyaviy ma'lumotlar bazasi — foydalanuvchilar, eventlar, topshiriqlar
- **Sprint (Event)**: Mukofotli musobaqa — tashkilotchi yaratadi, ishtirokchilar XP yig'adi
- **Leaderboard**: Tarantool'da TREE indeks yordamida real-vaqt reytingi
- **Idempotency_Lock**: Tarantool'da 3 soniyalik TTL bilan takroriy so'rovlarni bloklash mexanizmi
- **TMA**: Telegram Mini App — Telegram ichida ishlaydigan web ilova
- **HMAC_Validator**: X-Telegram-Init-Data sarlavhasini HMAC-SHA256 bilan tekshirish servisi
- **TON_Service**: TON blockchain bilan integratsiya servisi — depozit va tranzaksiya validatsiyasi
- **Anti_Fraud_Service**: Firbgarlikka qarshi tekshiruvlar servisi
- **Sync_Worker**: Tarantool'dan PostgreSQL'ga ma'lumotlarni asinxron sinxronlashtirish worker'i
- **State_Machine**: Sprint holat mashinkasi (DRAFT → PENDING_PAYMENT → ACTIVE → FINISHED)
- **Organizer**: Sprint tashkilotchisi — event yaratuvchi foydalanuvchi
- **Participant**: Sprint ishtirokchisi — eventga qo'shilgan foydalanuvchi
- **XP**: Experience Points — topshiriq bajarilganda beriladigan ochkolar
- **Telegram_ID**: Foydalanuvchini identifikatsiya qilish uchun yagona kalit (request.state.telegram_id dan olinadi)

---

## Talablar

### Talab 1: Xavfsiz Foydalanuvchi Identifikatsiyasi

**User Story:** Dasturchi sifatida, barcha API endpointlarida foydalanuvchi identifikatsiyasini xavfsiz amalga oshirishni xohlayman, shunda hech kim boshqa foydalanuvchi nomidan harakat qila olmasin.

#### Qabul Mezonlari

1. THE Backend SHALL barcha himoyalangan endpointlarda foydalanuvchi identifikatsiyasini faqat `request.state.telegram_id` orqali amalga oshirsin
2. WHEN so'rov `X-Telegram-Init-Data` sarlavhasini o'z ichiga olmasa, THE HMAC_Validator SHALL 401 Unauthorized xatosini qaytarsin
3. WHEN `X-Telegram-Init-Data` HMAC-SHA256 imzosi noto'g'ri bo'lsa, THE HMAC_Validator SHALL 401 Unauthorized xatosini qaytarsin
4. WHEN `X-Telegram-Init-Data` 5 daqiqadan eski bo'lsa (auth_date tekshiruvi), THE HMAC_Validator SHALL 401 Unauthorized xatosini qaytarsin
5. THE Backend SHALL hech qanday endpointda `user_id` yoki `telegram_id` ni query parametr yoki request body orqali qabul qilmasin — faqat middleware tomonidan `request.state` ga yozilgan qiymatdan foydalanilsin
6. WHEN HMAC validatsiya muvaffaqiyatli bo'lsa, THE HMAC_Validator SHALL foydalanuvchi ma'lumotlarini `request.state.telegram_user` va `request.state.telegram_id` ga yozsin

---

### Talab 2: Ma'lumotlar Bazasi Sxemasi va Upsert Logikasi

**User Story:** Dasturchi sifatida, to'liq va mustahkam DB sxemasini xohlayman, shunda dublikat yozuvlar paydo bo'lmasin va ma'lumotlar yaxlitligi saqlansin.

#### Qabul Mezonlari

1. THE Backend SHALL `users` jadvalida `telegram_id` ustuniga `UNIQUE` indeks o'rnatsin
2. WHEN foydalanuvchi botni qayta `/start` qilsa yoki yangi referal link bilan kirsa, THE Backend SHALL `Upsert` (INSERT ON CONFLICT UPDATE) logikasini qo'llasin — yangi qator ochilmasin
3. THE Backend SHALL `participants` jadvalida `(user_id, event_id)` kompozit `UNIQUE` kalitini saqlashda davom etsin
4. WHEN bir foydalanuvchi bitta eventga ikkinchi marta qo'shilmoqchi bo'lsa, THE Backend SHALL `IntegrityError` ni ushlash orqali 400 "User already joined this event" xatosini qaytarsin
5. THE Backend SHALL `user_task_completions` jadvalida `(user_id, task_id)` kompozit `UNIQUE` kalitini saqlashda davom etsin
6. WHEN foydalanuvchi bitta topshiriqni qayta bajarmoqchi bo'lsa, THE Backend SHALL 400 "Task already completed by user" xatosini qaytarsin
7. THE Backend SHALL referal ochkolarni faqat foydalanuvchi birinchi marta tizimga kirgandagina hisoblash logikasini amalga oshirsin

---

### Talab 3: Idempotency Lock Middleware (Tarantool)

**User Story:** Dasturchi sifatida, parallel takroriy so'rovlarni atomic tarzda bloklashni xohlayman, shunda race condition holatlari oldini olinsin.

#### Qabul Mezonlari

1. WHEN foydalanuvchi himoyalangan endpointga (POST/PUT) so'rov yuborsa, THE Idempotency_Lock SHALL Tarantool'da `lock:{telegram_id}:{path}:{method}` formatida atomic kalit yaratsin
2. THE Idempotency_Lock SHALL lock kalitiga 3 soniyalik TTL (Time-To-Live) o'rnatsin
3. WHEN lock kaliti allaqachon mavjud bo'lsa (parallel takroriy so'rov), THE Idempotency_Lock SHALL 429 Too Many Requests xatosini qaytarsin va so'rovni bazaga o'tkazmasin
4. WHEN lock TTL muddati tugasa, THE Idempotency_Lock SHALL lockni avtomatik ravishda o'chirsin
5. IF Tarantool ulanishi uzilsa, THEN THE Idempotency_Lock SHALL xatolikni log qilsin va so'rovni bloklamasdan o'tkazsin (graceful degradation)
6. THE Idempotency_Lock SHALL faqat POST va PUT metodlarini himoyalasin
7. THE Idempotency_Lock SHALL `/api/events`, `/api/tasks`, `/api/participants`, `/api/wallet` endpointlarini himoyalasin

---

### Talab 4: Tarantool Leaderboard Tizimi

**User Story:** Dasturchi sifatida, 10,000+ ishtirokchini real-vaqtda reytinglash uchun yuqori tezlikdagi in-memory leaderboard tizimini xohlayman, shunda foydalanuvchilar lag sezmasin.

#### Qabul Mezonlari

1. THE Tarantool SHALL `leaderboard` speys uchun TREE indeks yaratsin (XP bo'yicha saralangan)
2. WHEN foydalanuvchi topshiriqni muvaffaqiyatli bajarganda, THE Backend SHALL XP ni Tarantool'da O(log N) tezlikda yangilasin
3. THE Backend SHALL leaderboard so'rovlarini faqat Tarantool'dan o'qisin — PostgreSQL'ga leaderboard uchun murojaat qilmasin
4. THE Tarantool SHALL har bir event uchun alohida leaderboard saqlashni ta'minlasin (event_id, user_id, xp composite key)
5. WHEN leaderboard so'ralsa, THE Backend SHALL natijalarni XP bo'yicha kamayish tartibida (descending) qaytarsin
6. THE Backend SHALL leaderboard natijalarida foydalanuvchi user_id larini batch fetch orqali PostgreSQL'dan user ma'lumotlarini olsin (N+1 query muammosidan qochish)
7. THE Tarantool SHALL `sync_queue` speysi orqali XP o'zgarishlarini PostgreSQL'ga sinxronlash uchun navbatga qo'ysin

---

### Talab 5: PostgreSQL Asinxron Sync Worker

**User Story:** Dasturchi sifatida, Tarantool'dagi real-vaqt ma'lumotlarni PostgreSQL'ga ishonchli sinxronlashni xohlayman, shunda doimiy saqlash kafolatlansin.

#### Qabul Mezonlari

1. THE Sync_Worker SHALL Tarantool'dagi `sync_queue` dan "pending" statusli yozuvlarni batch tarzda o'qisin
2. THE Sync_Worker SHALL har bir batch da PostgreSQL'dagi `participants.total_xp` ustunini yangilasin
3. WHEN sinxronlash muvaffaqiyatli bo'lsa, THE Sync_Worker SHALL Tarantool'dagi yozuv statusini "completed" ga o'zgartirsin
4. IF sinxronlash davomida xatolik yuz bersa, THEN THE Sync_Worker SHALL xatoni log qilsin, rollback qilsin va keyingi iteratsiyada qayta urinsin
5. THE Sync_Worker SHALL har 5 soniyada ishlasin (konfiguratsiya orqali o'zgartirilishi mumkin)
6. THE Sync_Worker SHALL batch_size parametri orqali bir vaqtda qayta ishlanadigan yozuvlar sonini cheklasin (default: 100)

---

### Talab 6: REST API Endpointlari

**User Story:** Dasturchi sifatida, PRD da belgilangan barcha API endpointlarini to'liq implement qilishni xohlayman, shunda frontend bilan integratsiya ishlasin.

#### Qabul Mezonlari

1. THE Backend SHALL `GET /api/me` endpointini implement qilsin — joriy foydalanuvchi profili, statusi va ulangan hamyonini qaytarsin (`request.state.telegram_id` dan foydalanib)
2. THE Backend SHALL `GET /api/events` endpointini implement qilsin — faol va tugagan sprintlar ro'yxatini ixtiyoriy status filtri bilan qaytarsin
3. THE Backend SHALL `POST /api/events/:id/join` endpointini implement qilsin — foydalanuvchini sprintga ro'yxatdan o'tkazsin (Idempotency Lock va Anti-Fraud tekshiruvlaridan o'tkazib)
4. THE Backend SHALL `POST /api/tasks/:id/verify` endpointini implement qilsin — topshiriq bajarilganligini tekshirsin va XP qo'shsin
5. WHEN `GET /api/me` uchun foydalanuvchi topilmasa, THE Backend SHALL 404 xatosini qaytarsin
6. WHEN `POST /api/events/:id/join` uchun event ACTIVE statusida bo'lmasa, THE Backend SHALL 400 xatosini qaytarsin
7. WHEN `POST /api/tasks/:id/verify` uchun foydalanuvchi eventning ishtirokchisi bo'lmasa, THE Backend SHALL 403 xatosini qaytarsin
8. WHEN `POST /api/tasks/:id/verify` da topshiriq `verification_type` "channel_subscription" bo'lsa, THE Backend SHALL Telegram Bot API orqali `getChatMember` metodini chaqirib kanal a'zoligini tekshirsin

---

### Talab 7: Anti-Fraud Matritsasi

**User Story:** Dasturchi sifatida, bot fermalar va firbgarlikdan himoya qiluvchi ko'p qatlamli tekshiruv tizimini xohlayman, shunda faqat haqiqiy foydalanuvchilar qatnasha olsin.

#### Qabul Mezonlari

1. WHEN foydalanuvchining Telegram akkaunt yoshi 30 kundan kam bo'lsa, THE Anti_Fraud_Service SHALL 403 xatosini qaytarsin ("Account too young")
2. THE Anti_Fraud_Service SHALL Telegram Bot API `getChatMember` metodini chaqirib, foydalanuvchining majburiy kanallarga a'zoligini tekshirsin
3. WHEN foydalanuvchi majburiy kanaldan chiqib ketsa, THE Anti_Fraud_Service SHALL foydalanuvchining barcha XP ochkolarini nolga tushirsin (Tarantool va PostgreSQL da)
4. THE Anti_Fraud_Service SHALL Tarantool'da `ref:daily:{telegram_id}` kaliti ostida kunlik referal counter saqlash logikasini implement qilsin
5. WHEN foydalanuvchi bir sutkada 20 dan ortiq referal taklif qilsa, THE Anti_Fraud_Service SHALL yangi referallarni rad etsin
6. WHEN tashkilotchi o'zi yaratgan eventga qo'shilmoqchi bo'lsa, THE Backend SHALL 403 "Organizer cannot participate in their own event" xatosini qaytarsin
7. THE Anti_Fraud_Service SHALL `validate_user_for_event` metodida barcha tekshiruvlarni ketma-ket bajarib, birinchi muvaffaqiyatsiz tekshiruv sababi bilan rad etsin

---

### Talab 8: TON Blockchain Integratsiyasi — Hamyon Ulash

**User Story:** Dasturchi sifatida, foydalanuvchilar TON hamyonini xavfsiz ulash imkoniyatini xohlayman, shunda mukofotlar to'g'ri manzilga yuborilsin.

#### Qabul Mezonlari

1. WHEN foydalanuvchi hamyon ulash so'rovini yuborganda, THE TON_Service SHALL hamyon egaligini kriptografik imzo (signature) tekshiruvi orqali tasdiqlash
2. IF kriptografik imzo noto'g'ri bo'lsa, THEN THE TON_Service SHALL 401 "Invalid wallet signature" xatosini qaytarsin
3. WHEN hamyon egaligi tasdiqlansa, THE TON_Service SHALL hamyon balansini tekshirsin (minimum 0.1 TON)
4. IF hamyon balansi 0.1 TON dan kam bo'lsa, THEN THE TON_Service SHALL 400 "Insufficient wallet balance" xatosini qaytarsin
5. WHEN barcha tekshiruvlar muvaffaqiyatli bo'lsa, THE Backend SHALL foydalanuvchi profilida `wallet_address` ni saqlash
6. THE Backend SHALL hamyon ulash endpointida foydalanuvchini `request.state.telegram_id` orqali aniqlash — query param orqali emas

---

### Talab 9: TON Blockchain Integratsiyasi — Depozit Validatsiyasi

**User Story:** Dasturchi sifatida, tashkilotchi depozitini blokcheynda tekshirib, sprint aktivlashtirishni xohlayman, shunda faqat to'lov qilgan eventlar faol bo'lsin.

#### Qabul Mezonlari

1. WHEN tashkilotchi depozit tranzaksiya hash ni yuborganda, THE TON_Service SHALL TON API orqali tranzaksiyani blokcheynda tekshirsin
2. THE TON_Service SHALL tranzaksiya manzili smart-kontrakt manziliga to'g'ri kelishini tekshirsin
3. THE TON_Service SHALL tranzaksiya summasi kutilgan miqdorga teng yoki undan ko'p ekanligini tekshirsin
4. THE TON_Service SHALL tranzaksiya tasdiqlangan (confirmed) ekanligini tekshirsin
5. IF tranzaksiya validatsiyasi muvaffaqiyatsiz bo'lsa, THEN THE TON_Service SHALL 400 "Invalid deposit transaction" xatosini qaytarsin
6. WHEN depozit muvaffaqiyatli tasdiqlansa, THE Backend SHALL event statusini PENDING_PAYMENT dan ACTIVE ga o'zgartirsin va tx_hash ni saqlash
7. WHEN depozit so'rovini faqat event tashkilotchisi yuborishi mumkin bo'lsa, THE Backend SHALL boshqa foydalanuvchilar uchun 403 xatosini qaytarsin
8. WHEN event statusi PENDING_PAYMENT bo'lmasa, THE Backend SHALL 400 xatosini qaytarsin

---

### Talab 10: Sprint Holat Mashinkasi (State Machine)

**User Story:** Dasturchi sifatida, sprintning hayot siklini qat'iy holat mashinkasi orqali boshqarishni xohlayman, shunda noto'g'ri holatlar yuzaga kelmasin.

#### Qabul Mezonlari

1. THE State_Machine SHALL quyidagi holatlarni qo'llab-quvvatlasin: DRAFT → PENDING_PAYMENT → ACTIVE → FINISHED
2. WHILE event DRAFT holatida bo'lsa, THE Backend SHALL to'liq tahrirlash imkoniyatini bersin
3. WHEN tashkilotchi sozlashni yakunlasa, THE Backend SHALL eventni DRAFT dan PENDING_PAYMENT ga o'tkazsin va parametrlarni muzlatsin
4. WHILE event PENDING_PAYMENT holatida bo'lsa, THE Backend SHALL parametrlarni o'zgartirishni taqiqlasin
5. WHEN depozit tasdiqlansa, THE Backend SHALL eventni PENDING_PAYMENT dan ACTIVE ga o'tkazsin
6. WHILE event ACTIVE holatida bo'lsa, THE Backend SHALL hech qanday parametr o'zgartirishga ruxsat bermasin
7. WHEN event muddati (end_date) tugasa, THE Backend SHALL eventni ACTIVE dan FINISHED ga avtomat o'tkazsin
8. WHILE event FINISHED holatida bo'lsa, THE Backend SHALL hech qanday o'zgartirishga ruxsat bermasin
9. IF noto'g'ri holat o'tishi so'ralsa (masalan DRAFT → ACTIVE), THEN THE Backend SHALL 400 xatosini qaytarsin

---

### Talab 11: Background Worker — Kanal Obunasi Cron Vazifasi

**User Story:** Dasturchi sifatida, ishtirokchilarning kanal obunalarini davriy tekshirib turuvchi avtomatik vazifani xohlayman, shunda firbgarlar aniqlansa XP lari olib qo'yilsin.

#### Qabul Mezonlari

1. THE Backend SHALL kundalik asinxron Cron vazifasini implement qilsin — barcha ACTIVE eventlardagi ishtirokchilarning kanal obunasini tekshirish uchun
2. WHEN Cron vazifasi ishtirokchining kanaldan chiqib ketganini aniqlasa, THE Backend SHALL Tarantool'dagi XP ni nolga tushirsin
3. WHEN Cron vazifasi ishtirokchining kanaldan chiqib ketganini aniqlasa, THE Backend SHALL PostgreSQL'dagi `participants.total_xp` ni nolga tushirsin
4. THE Backend SHALL Telegram Bot API `getChatMember` metodini rate limit ga rioya qilib chaqirsin (saniyasiga max 30 so'rov)
5. IF Telegram API chaqiruvi muvaffaqiyatsiz bo'lsa, THEN THE Backend SHALL xatoni log qilsin va keyingi iteratsiyada qayta urinsin

---

### Talab 12: Background Worker — Event Auto-Finish

**User Story:** Dasturchi sifatida, muddati tugagan eventlarni avtomatik yakunlaydigan worker ni xohlayman, shunda qo'lda aralashmasdan sprintlar to'g'ri tugasin.

#### Qabul Mezonlari

1. THE Backend SHALL davriy (har 60 soniyada) ACTIVE eventlarni tekshiruvchi worker ni implement qilsin
2. WHEN event ning `end_date` vaqti o'tgan bo'lsa, THE Backend SHALL event statusini ACTIVE dan FINISHED ga o'zgartirsin
3. WHEN event FINISHED holatiga o'tkazilsa, THE Backend SHALL Tarantool'dan Top-N g'oliblar ro'yxatini olsin va saqlash
4. IF event da birorta ham ishtirokchi bo'lmasa, THEN THE Backend SHALL eventni FINISHED ga o'tkazsin va g'oliblar ro'yxatini bo'sh qoldirsin

---

### Talab 13: Telegram Bot API Integratsiyasi

**User Story:** Dasturchi sifatida, Telegram Bot API bilan to'liq ishlaydigan integratsiyani xohlayman, shunda kanal obunasi tekshiruvi va boshqa funksiyalar ishlashi mumkin bo'lsin.

#### Qabul Mezonlari

1. THE Backend SHALL Telegram Bot API `getChatMember` metodini async tarzda chaqirish logikasini implement qilsin
2. WHEN `getChatMember` "member", "administrator" yoki "creator" statusini qaytarsa, THE Backend SHALL foydalanuvchini obunachi deb belgilasin
3. WHEN `getChatMember` "left" yoki "kicked" statusini qaytarsa, THE Backend SHALL foydalanuvchini obunachi emas deb belgilasin
4. IF Telegram API rate limit ga urilsa (429), THEN THE Backend SHALL `Retry-After` sarlavhasida ko'rsatilgan vaqtgacha kutib, qayta urinsin
5. THE Backend SHALL Telegram Bot Token ni `.env` faylidan environment variable orqali olsin

---

### Talab 14: Xatoliklarni Boshqarish va Logging

**User Story:** Dasturchi sifatida, tizimli xatoliklarni boshqarish va logging tizimini xohlayman, shunda muammolarni tez aniqlash va debug qilish mumkin bo'lsin.

#### Qabul Mezonlari

1. THE Backend SHALL barcha API endpointlarida aniq va informatif xato xabarlarini qaytarsin (masalan: "Event not found", "User already joined this event")
2. THE Backend SHALL barcha muhim operatsiyalarni (wallet connect, deposit, join, verify) log qilsin
3. IF kutilmagan xatolik yuz bersa, THEN THE Backend SHALL 500 Internal Server Error qaytarsin va xatolik tafsilotlarini foydalanuvchiga ko'rsatmasin
4. THE Backend SHALL `IntegrityError` ni ushlash orqali bazadagi constraint violation larni user-friendly xabar bilan qaytarsin
5. THE Backend SHALL Tarantool ulanishi xatoliklarini alohida log qilsin va graceful degradation ta'minlasin

---

### Talab 15: Konfiguratsiya va Environment Boshqaruvi

**User Story:** Dasturchi sifatida, barcha maxfiy kalitlar va konfiguratsiyalarni xavfsiz boshqarishni xohlayman, shunda production muhitda xavfsizlik ta'minlansin.

#### Qabul Mezonlari

1. THE Backend SHALL barcha maxfiy kalitlarni (bot token, TON API key, DB credentials) `.env` faylidan o'qisin
2. THE Backend SHALL `pydantic-settings` orqali environment variable larni validatsiya qilsin
3. THE Backend SHALL smart-kontrakt manzilini konfiguratsiyada saqlash (hardcode qilmaslik)
4. THE Backend SHALL `debug` rejimida tafsilotli loglarni chiqarsin, production da esa cheklangan loglarni
5. IF majburiy environment variable topilmasa, THEN THE Backend SHALL dastur ishga tushganda aniq xatolik xabari bilan to'xtasin
