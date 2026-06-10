# Requirements Document — PrizeRace Frontend Developer Texnik Vazifasi (TZ)

## Kirish

Ushbu hujjat PrizeRace Telegram Mini App platformasining frontend qismini to'liq ishlab chiqish uchun texnik talablarni belgilaydi. PrizeRace — geymifikatsiyalangan sprint musobaqalari platformasi bo'lib, foydalanuvchilar topshiriqlarni bajarib XP yig'adilar va TON kriptovalyutasida mukofot yutadilar. Frontend React 18 + TypeScript + Vite + TailwindCSS + Zustand + TanStack Query + @tonconnect/ui-react texnologiyalarida quriladi. Loyiha hozirda ~60% tayyor bo'lib, routing, organizer UI, to'liq xato boshqaruvi va boshqa muhim funksiyalar yetishmaydi.

## Glossary

- **Ilova**: PrizeRace Telegram Mini App frontend ilovasi
- **Router**: React Router v6 kutubxonasi yordamida sahifalar o'rtasida navigatsiya tizimi
- **Sprint**: Tashkilotchi tomonidan yaratilgan vaqt chegarali musobaqa (event)
- **Leaderboard**: Sprint ishtirokchilarining XP bo'yicha saralangan jonli reytingi
- **Tashkilotchi**: Sprint yaratan va mukofot fondini to'lagan foydalanuvchi
- **Ishtirokchi**: Sprintga qo'shilgan va topshiriqlarni bajarayotgan foydalanuvchi
- **Topshiriq**: Sprint doirasida bajariladigan vazifa (kanal obunasi, referal va hokazo)
- **XP**: Topshiriqni bajarish natijasida beriladigan tajriba ochkolari
- **TON_Connect**: TON blokcheyn hamyonini ulash uchun ishlatiladigan SDK (@tonconnect/ui-react)
- **TanStack_Query**: Server holatini boshqarish, keshlash va sinxronizatsiya kutubxonasi
- **Zustand**: Yengil va tezkor client-side holat boshqaruvchisi (state manager)
- **Axios_Interceptor**: HTTP so'rov va javoblarni global darajada tutib qolish mexanizmi
- **Toast**: Foydalanuvchiga qisqa muddatli bildirishnoma ko'rsatuvchi UI komponenti
- **Skeleton_Loader**: Ma'lumot yuklanayotganda kontent shaklidagi animatsion placeholder
- **Virtualizatsiya**: Katta ro'yxatlarni faqat ko'rinadigan elementlarni renderlab ko'rsatish texnikasi (react-window)
- **Double_Click_Himoya**: Tugma bosilgandan keyin so'rov tugaguncha qayta bosishni bloklash mexanizmi
- **Telegram_WebApp**: Telegram Mini App SDK interfeysi (window.Telegram.WebApp)
- **HapticFeedback**: Telegram WebApp orqali qurilmada tebranish effektini ishga tushirish
- **BackButton**: Telegram Mini App yuqori chap burchagidagi "Orqaga" tugmasi
- **MainButton**: Telegram Mini App pastki qismidagi asosiy tugma
- **Proof_Alignment**: TON hamyonni ulashda kriptografik imzo tekshiruvi
- **Idempotentlik**: Bir xil so'rovni qayta yuborishda tizim holatining o'zgarmasligi

---

## Talablar

### Talab 1: React Router navigatsiya tizimini o'rnatish

**User Story:** Men (frontend developer) sifatida, ilovaga React Router v6 o'rnatmoqchiman, shunda foydalanuvchilar sahifalar o'rtasida URL orqali navigatsiya qila olsin va brauzer tarixi to'g'ri ishlaydi.

#### Qabul mezonlari

1. THE Ilova SHALL React Router v6 (react-router-dom) kutubxonasini BrowserRouter orqali ildiz darajasida ulangan holda ishga tushirsin
2. THE Router SHALL quyidagi marshrut (route) yo'llarini qo'llab-quvvatlasin: "/" (bosh sahifa), "/event/:id" (sprint tafsilotlari), "/event/:id/leaderboard" (to'liq reyting), "/profile" (profil), "/organizer" (tashkilotchi paneli), "/organizer/create" (sprint yaratish)
3. WHEN foydalanuvchi mavjud bo'lmagan URL manzilga o'tsa, THE Router SHALL 404 NotFound sahifasini ko'rsatsin va bosh sahifaga qaytish tugmasini taqdim etsin
4. THE Router SHALL autentifikatsiya qilinmagan foydalanuvchini himoyalangan sahifalarga kirishda bosh sahifaga yo'naltirsin (redirect)
5. WHEN sahifa o'zgarganda, THE Ilova SHALL Telegram BackButton ko'rinishini yangilasin — bosh sahifada yashirin, boshqa sahifalarda ko'rinuvchan

---

### Talab 2: Bosh sahifa (HomePage) sprint ro'yxati

**User Story:** Men (ishtirokchi) sifatida, ilovani ochganimda faol va tugallangan sprintlar ro'yxatini ko'rmoqchiman, shunda qaysi musobaqalarga qatnashish mumkinligini tezda bilaman.

#### Qabul mezonlari

1. WHEN bosh sahifa yuklanganda, THE Ilova SHALL TanStack_Query orqali "ACTIVE" statusidagi sprintlar ro'yxatini so'rab olib, kesh muddatini 30 soniya qilib belgilasin
2. THE Ilova SHALL har bir sprint kartochkasida quyidagi ma'lumotlarni ko'rsatsin: sarlavha, tavsif (2 qatorgacha), status badge, mukofot fondi (TON), g'oliblar soni (Top-N) va tugash vaqtigacha qolgan countdown timer
3. WHILE ma'lumotlar yuklanayotgan vaqtda, THE Ilova SHALL sprint kartochkasi shaklidagi Skeleton_Loader animatsiyasini ko'rsatsin (kamida 3 ta placeholder kartochka)
4. WHEN sprint ro'yxati bo'sh bo'lganda, THE Ilova SHALL "Hozircha faol musobaqalar yo'q" xabarini mos ikonka bilan ko'rsatsin
5. THE Ilova SHALL sprintlarni ikkita tab orqali filtrlash imkonini bersin: "Faol" va "Tugallangan"
6. WHEN foydalanuvchi sprint kartochkasini bossa, THE Router SHALL "/event/:id" sahifasiga yo'naltirsin

---

### Talab 3: Sprint tafsilotlari sahifasi (EventDetailPage)

**User Story:** Men (ishtirokchi) sifatida, tanlangan sprint haqida to'liq ma'lumot ko'rmoqchiman, shunda topshiriqlarni bajarishni boshlashim mumkin.

#### Qabul mezonlari

1. WHEN "/event/:id" sahifasi ochilganda, THE Ilova SHALL TanStack_Query orqali sprint ma'lumotlarini, topshiriqlar ro'yxatini va joriy leaderboard-ning Top-10 ni parallel ravishda so'rab olsin
2. THE Ilova SHALL sprint tafsilotlari sahifasida quyidarni ko'rsatsin: sarlavha, to'liq tavsif, status, mukofot fondi, g'oliblar soni, boshlanish va tugash sanalari, countdown progress bar
3. THE Ilova SHALL topshiriqlar ro'yxatini ko'rsatsin — har bir topshiriq uchun sarlavha, tavsif, XP mukofoti va bajarilganlik holati (tugallangan/tugallanmagan) aniq ko'rinsin
4. WHEN ishtirokchi "Tekshirish" tugmasini bossa, THE Ilova SHALL POST /api/tasks/:id/verify endpointiga so'rov yuborsin va natijaga qarab XP yangilanishini ko'rsatsin
5. THE Ilova SHALL sahifaning pastki qismida "To'liq Reyting" tugmasini ko'rsatsin, bosilganda "/event/:id/leaderboard" sahifasiga o'tsin
6. WHEN sprint statusi "ACTIVE" bo'lganda va foydalanuvchi hali ishtirok etmagan bo'lsa, THE Ilova SHALL "Qatnashish" tugmasini ko'rsatsin
7. IF sprint statusi "FINISHED" bo'lsa, THEN THE Ilova SHALL g'oliblar ro'yxatini va mukofot taqsimotini ko'rsatsin

---

### Talab 4: Leaderboard sahifasi virtualizatsiya bilan

**User Story:** Men (ishtirokchi) sifatida, sprintdagi barcha ishtirokchilar reytingini lag'siz ko'rmoqchiman, hatto 10 000+ ishtirokchi bo'lsa ham.

#### Qabul mezonlari

1. THE Ilova SHALL leaderboard sahifasida react-window (FixedSizeList) orqali virtualizatsiyani qo'llasin — faqat ko'rinadigan qatorlar DOM ga render qilinsin
2. WHEN leaderboard ma'lumotlari yuklanayotganda, THE Ilova SHALL markazda Spinner va "Reyting yuklanmoqda..." matnini ko'rsatsin
3. THE Ilova SHALL har bir qatorda reyting o'rni (1-3 o'rinlar uchun medal emoji), foydalanuvchi nomi, hamyon manzili (qisqartirilgan), va XP balini ko'rsatsin
4. WHEN joriy foydalanuvchi ro'yxatda bo'lsa, THE Ilova SHALL uning qatorini alohida rang bilan ajratib ko'rsatsin va "SIZ" belgisini qo'shsin
5. THE Ilova SHALL 10 000 ta elementni 60 FPS da muammosiz aylantira (scroll) olsin — har bir qator balandligi 72px qilib belgilansin
6. WHEN foydalanuvchi sahifa yuqorisiga qaytsa (scroll to top), THE Ilova SHALL animatsion tarzda yuqoriga aylantirsin

---

### Talab 5: Profil sahifasi (ProfilePage)

**User Story:** Men (foydalanuvchi) sifatida, o'z profilimni ko'rmoqchiman — ulangan hamyonim, ishtirok etgan sprintlarim va umumiy XP balim ko'rinsin.

#### Qabul mezonlari

1. WHEN "/profile" sahifasi ochilganda, THE Ilova SHALL foydalanuvchi ma'lumotlarini (ism, username, avatar, hamyon manzili, yaratilgan sana) ko'rsatsin
2. THE Ilova SHALL foydalanuvchi ishtirok etgan sprintlar ro'yxatini ko'rsatsin — har birida sprint nomi, holati va yig'ilgan XP bali ko'rinsin
3. WHEN hamyon ulangan bo'lsa, THE Ilova SHALL hamyon manzilini qisqartirilgan formatda (6...4 belgi) ko'rsatsin va "Uzish" tugmasini taqdim etsin
4. WHEN hamyon ulanmagan bo'lsa, THE Ilova SHALL "Hamyonni ulash" tugmasini ko'rsatsin, bosilganda TON_Connect oynasini ochsin
5. THE Ilova SHALL Telegram mavzu ranglariga (dark/light theme) moslashgan ko'rinishda render qilinsin

---

### Talab 6: TON Connect integratsiyasi va hamyon ulash

**User Story:** Men (foydalanuvchi) sifatida, TON hamyonimni ilovaga ulashni xohlayman, shunda musobaqa yutganimda mukofotni avtomatik olaman.

#### Qabul mezonlari

1. THE Ilova SHALL ildiz darajasida (main.tsx) TonConnectUIProvider komponentini manifestUrl parametri bilan o'rnatilgan holda ishga tushirsin
2. WHEN foydalanuvchi "Hamyonni ulash" tugmasini bossa, THE Ilova SHALL TON_Connect modal oynasini ochsin va mavjud hamyon ilovalarini ko'rsatsin
3. WHEN hamyon muvaffaqiyatli ulanganda, THE Ilova SHALL kriptografik imzo (Proof_Alignment) orqali hamyon egaligini tasdiqlashni so'rasin
4. WHEN Proof_Alignment tasdiqlanganda, THE Ilova SHALL POST /api/me/wallet endpointiga hamyon manzili va imzoni yuborsin
5. IF backend hamyonni muvaffaqiyatli saqlasa, THEN THE Ilova SHALL "Hamyon ulandi ✓" muvaffaqiyat xabarini Toast orqali ko'rsatsin va profil ma'lumotlarini yangilasin
6. IF hamyon ulash jarayonida xatolik yuz bersa, THEN THE Ilova SHALL aniq xato xabarini ko'rsatsin va qayta urinish imkonini bersin

---

### Talab 7: Double-click (ikki marta bosish) himoyasi

**User Story:** Men (tizim administratori) sifatida, foydalanuvchilar tugmani tez-tez bosib serverga ortiqcha so'rov yubormasligini xohlayman, shunda tizim barqaror ishlaydi.

#### Qabul mezonlari

1. WHEN foydalanuvchi "Qatnashish" tugmasini bossa, THE Ilova SHALL tugmani darhol disabled holatga o'tkazsin va spinner animatsiyasini ko'rsatsin
2. WHILE server so'rovi bajarilayotganda, THE Ilova SHALL tugmaning disabled holatini saqlasin — qayta bosish imkonsiz bo'lsin
3. WHEN server javobi (muvaffaqiyat yoki xatolik) kelganda, THE Ilova SHALL tugma holatini mos ravishda yangilasin
4. THE Ilova SHALL "Tekshirish" (verify), "Qatnashish" (join), "Hamyonni ulash" (connect wallet), va "Sprint yaratish" (create event) tugmalarida Double_Click_Himoya mexanizmini joriy etsin
5. WHEN foydalanuvchi allaqachon qatnashgan bo'lsa, THE Ilova SHALL "Qatnashish" tugmasi o'rniga "✓ Siz allaqachon qatnashyapsiz" matnini disabled holatda ko'rsatsin

---

### Talab 8: Backend xatolarini global darajada boshqarish (Axios Interceptors)

**User Story:** Men (foydalanuvchi) sifatida, server xatoliklari haqida aniq va tushunarli xabar olmoqchiman, shunda nima qilishim kerakligini bilaman.

#### Qabul mezonlari

1. THE Ilova SHALL Axios response interceptor orqali barcha server javoblarini global darajada kuzatsin
2. WHEN backend 400 "already joined" xatosini qaytarsa, THE Axios_Interceptor SHALL xato xabarini tutib, tegishli UI komponentiga "Siz allaqachon qatnashyapsiz" holatini yetkazsin
3. WHEN backend 429 "Too Many Requests" xatosini qaytarsa, THE Axios_Interceptor SHALL Toast orqali "Iltimos kuting, so'rovingiz ishlanmoqda" bildirishnomasini ko'rsatsin
4. WHEN backend 403 xatosini "account too young" sababi bilan qaytarsa, THE Ilova SHALL maxsus ogohlantirish ekranini ko'rsatsin — akkaunt yoshi 30 kundan kam ekanligi haqida xabar va qachon qayta urinish mumkinligi ko'rsatilsin
5. IF tarmoq ulanishi yo'qolsa (network error), THEN THE Ilova SHALL "Internet aloqasi yo'q" xabarini va "Qayta urinish" tugmasini ko'rsatsin
6. WHEN backend 500 xatosini qaytarsa, THE Ilova SHALL "Server xatoligi yuz berdi, iltimos keyinroq urinib ko'ring" xabarini ko'rsatsin

---

### Talab 9: Tashkilotchi paneli (OrganizerDashboard)

**User Story:** Men (tashkilotchi) sifatida, o'zim yaratgan sprintlarni boshqarmoqchiman — yangi sprint yaratish, tahrirlash va depozit to'lash imkoni bo'lsin.

#### Qabul mezonlari

1. WHEN "/organizer" sahifasi ochilganda, THE Ilova SHALL foydalanuvchi yaratgan barcha sprintlar ro'yxatini status bo'yicha guruhlangan holda ko'rsatsin (DRAFT, PENDING_PAYMENT, ACTIVE, FINISHED)
2. THE Ilova SHALL har bir sprint kartochkasida status badge, sarlavha, mukofot fondi, va sanalarni ko'rsatsin
3. WHEN tashkilotchi "Yangi Sprint" tugmasini bossa, THE Router SHALL "/organizer/create" sahifasiga yo'naltirsin
4. WHEN sprint "DRAFT" statusida bo'lganda, THE Ilova SHALL "Tahrirlash" va "To'lovga o'tkazish" tugmalarini ko'rsatsin
5. WHEN sprint "PENDING_PAYMENT" statusida bo'lganda, THE Ilova SHALL "Depozit to'lash" tugmasini ko'rsatsin
6. WHEN sprint "ACTIVE" yoki "FINISHED" statusida bo'lganda, THE Ilova SHALL tahrirlash va o'zgartirish tugmalarini yashirsin — faqat ko'rish rejimi

---

### Talab 10: Sprint yaratish formasi (CreateEventPage)

**User Story:** Men (tashkilotchi) sifatida, yangi sprint yaratishni xohlayman — sarlavha, tavsif, topshiriqlar, mukofot fondi, sanalar va g'oliblar sonini kiritib.

#### Qabul mezonlari

1. THE Ilova SHALL sprint yaratish formasida quyidagi maydonlarni taqdim etsin: sarlavha (majburiy, 5-100 belgi), tavsif (ixtiyoriy, 500 belgigacha), mukofot fondi TON da (majburiy, minimal 1 TON), g'oliblar soni Top-N (majburiy, 1-100), boshlanish sanasi, tugash sanasi
2. THE Ilova SHALL forma doirasida kamida bitta topshiriq qo'shish imkonini bersin — har bir topshiriq uchun sarlavha, tavsif, XP mukofoti va tekshirish turi (channel_subscription, referral, custom) kiritilsin
3. WHEN forma validatsiyadan muvaffaqiyatli o'tsa va "Yaratish" tugmasi bosilsa, THE Ilova SHALL POST /api/events endpointiga so'rov yuborsin va muvaffaqiyatda tashkilotchi panelga yo'naltirsin
4. IF tugash sanasi boshlanish sanasidan oldin tanlansa, THEN THE Ilova SHALL "Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak" xato xabarini ko'rsatsin
5. IF forma validatsiyadan o'tmasa, THEN THE Ilova SHALL xato bo'lgan maydonlar yonida qizil rang bilan xato xabarini ko'rsatsin
6. WHILE forma yuborilayotganda, THE Ilova SHALL "Yaratish" tugmasini disabled qilib spinner ko'rsatsin (Double_Click_Himoya)

---

### Talab 11: Depozit to'lash oqimi (Deposit Flow UI)

**User Story:** Men (tashkilotchi) sifatida, sprintni faollashtirish uchun TON depozitini to'lamoqchiman, shunda sprint ishtirokchilarga ko'rinadi.

#### Qabul mezonlari

1. WHEN tashkilotchi "Depozit to'lash" tugmasini bossa, THE Ilova SHALL depozit oqimini boshlasin — avval hamyon ulangan yoki ulanmaganligini tekshirsin
2. IF hamyon ulanmagan bo'lsa, THEN THE Ilova SHALL avval TON_Connect orqali hamyon ulashni taklif qilsin
3. WHEN hamyon ulangan bo'lsa, THE Ilova SHALL to'lov ma'lumotlarini ko'rsatsin: sprint sarlavhasi, kerakli summa (TON), va smart-kontrakt manzili
4. WHEN tashkilotchi "To'lash" tugmasini bossa, THE Ilova SHALL TON_Connect SDK orqali tranzaksiyani imzolash va yuborish oynasini ochsin
5. WHEN tranzaksiya muvaffaqiyatli yuborilganda, THE Ilova SHALL tranzaksiya hash-ini backend POST /api/wallet/deposit endpointiga yuborsin va tasdiqlash kutsin
6. WHILE backend tranzaksiyani tekshirayotganda, THE Ilova SHALL "Tranzaksiya tekshirilmoqda..." holat ko'rsatkichini (progress indicator) ko'rsatsin
7. WHEN backend tasdiqlasa, THE Ilova SHALL "Sprint muvaffaqiyatli faollashtirildi! ✓" xabarini ko'rsatsin va tashkilotchi paneliga yo'naltirsin
8. IF tranzaksiya tasdiqlanmasa, THEN THE Ilova SHALL "Tranzaksiya tasdiqlanmadi, iltimos qayta urinib ko'ring" xabarini ko'rsatsin

---

### Talab 12: TanStack Query bilan ma'lumotlarni boshqarish

**User Story:** Men (frontend developer) sifatida, barcha API chaqiruvlarini TanStack Query orqali boshqarmoqchiman, shunda keshlash, qayta so'rash va optimistik yangilanishlar to'g'ri ishlaydi.

#### Qabul mezonlari

1. THE Ilova SHALL main.tsx da QueryClientProvider ni ildiz darajasida o'rnatilgan holda ishga tushirsin — default staleTime 30 soniya, retry 2 marta
2. THE Ilova SHALL barcha GET so'rovlarini useQuery hook orqali bajarsin — har bir so'rov uchun queryKey aniq belgilansin
3. THE Ilova SHALL barcha POST/PUT/DELETE so'rovlarini useMutation hook orqali bajarsin — muvaffaqiyatda tegishli query cache invalidate qilinsin
4. WHEN foydalanuvchi sprintga qo'shilganda, THE Ilova SHALL optimistik yangilanish (optimistic update) qo'llasin — UI darhol yangilansin, xatoda esa rollback qilsin
5. THE Ilova SHALL eventlar ro'yxatini 30 soniyada bir marta avtomatik qayta so'rasin (refetchInterval) — faqat sahifa faol bo'lganda
6. WHEN foydalanuvchi ilovani background-dan foreground-ga qaytarsa, THE Ilova SHALL barcha faol so'rovlarni qayta yuborsin (refetchOnWindowFocus)

---

### Talab 13: Zustand bilan client-side holat boshqaruvi

**User Story:** Men (frontend developer) sifatida, autentifikatsiya va UI holatini Zustand orqali boshqarmoqchiman, shunda komponentlar o'rtasida holat tez va samarali almashiladi.

#### Qabul mezonlari

1. THE Ilova SHALL authStore da quyidagi holatlarni boshqarsin: user (joriy foydalanuvchi), telegramUser (Telegram ma'lumotlari), isAuthenticated, isLoading, error
2. THE Ilova SHALL uiStore yaratsin — quyidagi holatlarni boshqarsin: activeTab (joriy tab), theme (dark/light), toasts ro'yxati, isSidebarOpen
3. WHEN foydalanuvchi login qilganda, THE Ilova SHALL authStore dagi user holatini yangilasin va isAuthenticated ni true qilib belgilasin
4. THE Ilova SHALL Zustand store-lardan faqat kerakli field-larni selector orqali olsin — ortiqcha re-render bo'lmasin
5. WHEN toast qo'shilganda, THE Ilova SHALL uni 3 soniyadan keyin avtomatik o'chirsin (auto-dismiss)

---

### Talab 14: Telegram Mini App integratsiyasi

**User Story:** Men (foydalanuvchi) sifatida, ilova Telegram ichida tabiiy va muammosiz ishlashini xohlayman — tema ranglari, tugmalar va tebranish effektlari mos bo'lsin.

#### Qabul mezonlari

1. WHEN ilova yuklanganda, THE Ilova SHALL Telegram_WebApp.ready() va expand() metodlarini chaqirsin — ilova to'liq ekranga kengaysin
2. THE Ilova SHALL Telegram mavzusidan (colorScheme) dark yoki light rejimini aniqlasab, UI ranglarini mos ravishda moslashtirilsin
3. WHEN foydalanuvchi bosh sahifadan boshqa sahifaga o'tsa, THE Ilova SHALL Telegram BackButton ni ko'rsatsin va bosilganda oldingi sahifaga qaytarsin
4. WHEN foydalanuvchi muhim amal bajarsa (join, verify, wallet connect), THE Ilova SHALL HapticFeedback.impactOccurred('medium') orqali tebranish effektini ishga tushirsin
5. THE Ilova SHALL Telegram WebApp viewport balandligini (viewportHeight, viewportStableHeight) hisobga olsin — kontent pastki panel ostida qolmasligi uchun padding qo'shilsin
6. WHERE MainButton kerak bo'lgan oqimlarda (masalan depozit sahifasi), THE Ilova SHALL Telegram MainButton ni matn va rang bilan sozlab ko'rsatsin

---

### Talab 15: Anti-Fraud UX — Akkaunt yoshi bloklash ekrani

**User Story:** Men (tizim) sifatida, 30 kundan kam yosh akkauntlarni sprintlarga kiritmaslikni xohlayman, shunda soxta akkauntlar oldini olinadi.

#### Qabul mezonlari

1. WHEN backend 403 xatosini "account_too_young" sababi bilan qaytarsa, THE Ilova SHALL maxsus bloklash ekranini ko'rsatsin
2. THE Ilova SHALL bloklash ekranida quyidagilarni ko'rsatsin: ogohlantirish ikonkasi, "Akkauntingiz juda yosh" sarlavhasi, akkaunt yaratilgan sana, qachon (necha kun qolganini) qayta urinish mumkinligi
3. THE Ilova SHALL bloklash ekranida "Tushundim" tugmasini ko'rsatsin — bosilganda bosh sahifaga qaytarsin
4. WHILE bloklash ekrani ko'rsatilayotganda, THE Ilova SHALL boshqa navigatsiya imkoniyatlarini cheklasin — faqat bosh sahifaga qaytish mumkin bo'lsin

---

### Talab 16: Anti-Fraud UX — Tashkilotchi cheklovi

**User Story:** Men (tizim) sifatida, tashkilotchining o'zi yaratgan sprintga qatnashishini oldini olmoqchiman, shunda manfaatlar to'qnashuvi bo'lmaydi.

#### Qabul mezonlari

1. WHEN sprint tafsilotlari sahifasida sprint organizer_id joriy foydalanuvchi id-ga teng bo'lsa, THE Ilova SHALL "Qatnashish" tugmasini ko'rsatmasin
2. WHEN tashkilotchi o'z sprintini ko'rayotganda, THE Ilova SHALL "Siz bu sprintning tashkilotchisisiz" xabarini ko'rsatsin
3. THE Ilova SHALL tashkilotchiga faqat reyting va statistika ko'rish imkonini bersin — ishtirok etish funksiyalari yashirilsin

---

### Talab 17: Kanal obunasi tekshiruvi UI

**User Story:** Men (ishtirokchi) sifatida, topshiriq sifatida kanal obunasini tekshirishni xohlayman, shunda XP olaman.

#### Qabul mezonlari

1. WHEN topshiriq turi "channel_subscription" bo'lganda, THE Ilova SHALL kerakli kanal nomini va havolasini ko'rsatsin
2. THE Ilova SHALL "Kanalga o'tish" tugmasini ko'rsatsin — bosilganda Telegram ichida kanal sahifasi ochilsin
3. WHEN foydalanuvchi "Tekshirish" tugmasini bossa, THE Ilova SHALL POST /api/tasks/:id/verify endpointiga so'rov yuborsin
4. WHEN backend muvaffaqiyat qaytarsa, THE Ilova SHALL topshiriq kartochkasini "✓ Bajarildi" holatiga o'tkazsin va yig'ilgan XP ni yangilasin
5. IF backend obuna tasdiqlanmasa (foydalanuvchi hali obuna bo'lmagan), THEN THE Ilova SHALL "Avval kanalga obuna bo'ling" xabarini ko'rsatsin
6. WHILE tekshirish so'rovi bajarilayotganda, THE Ilova SHALL "Tekshirish" tugmasini disabled qilib spinner ko'rsatsin (Double_Click_Himoya)

---

### Talab 18: Skeleton Loader va yuklanish holatlari

**User Story:** Men (foydalanuvchi) sifatida, ma'lumot yuklanayotganda bo'sh ekran emas, balki kontent shaklidagi animatsion placeholder ko'rmoqchiman, shunda ilova professional ko'rinadi.

#### Qabul mezonlari

1. WHILE sprint ro'yxati yuklanayotganda, THE Ilova SHALL 3 ta sprint kartochkasi shaklidagi Skeleton_Loader animatsiyasini ko'rsatsin
2. WHILE leaderboard yuklanayotganda, THE Ilova SHALL 5 ta qator shaklidagi Skeleton_Loader ko'rsatsin
3. WHILE profil sahifasi yuklanayotganda, THE Ilova SHALL avatar, ism va statistika bloklari shaklidagi Skeleton_Loader ko'rsatsin
4. THE Ilova SHALL Skeleton_Loader komponentida pulse animatsiyasi (animate-pulse) ni qo'llasin — ranglari asosiy fon bilan uyg'un bo'lsin
5. WHEN ma'lumot muvaffaqiyatli yuklanganda, THE Ilova SHALL Skeleton_Loader dan haqiqiy kontentga silliq o'tish (transition) ko'rsatsin

---

### Talab 19: Xatolik holatlari va qayta urinish

**User Story:** Men (foydalanuvchi) sifatida, xatolik yuz berganda tushunarli xabar va qayta urinish imkoni olmoqchiman, shunda muammoni o'zim hal qila olaman.

#### Qabul mezonlari

1. WHEN API so'rovi muvaffaqiyatsiz tugasa, THE Ilova SHALL xatolik xabarini ko'rsatsin va "Qayta urinish" tugmasini taqdim etsin
2. THE Ilova SHALL ErrorBoundary komponentini ildiz darajasida o'rnatsin — kutilmagan JavaScript xatoliklarini tutib, fallback UI ko'rsatsin
3. WHEN ErrorBoundary xatoni tutganda, THE Ilova SHALL xato xabarini, "Sahifani yangilash" tugmasini va texnik tafsilotlarni (collapsed) ko'rsatsin
4. THE Ilova SHALL TanStack_Query retry mexanizmini qo'llasin — muvaffaqiyatsiz so'rovlar 2 marta qayta urinilsin (1 soniya va 3 soniya oraliqda)
5. IF 3 marta ketma-ket xatolik yuz bersa, THEN THE Ilova SHALL "Server bilan aloqa o'rnatilmadi" xabarini ko'rsatsin va qo'lda qayta urinish tugmasini taqdim etsin

---

### Talab 20: Responsive va Mobile-first dizayn

**User Story:** Men (foydalanuvchi) sifatida, ilova telefonimda mukammal ko'rinishini xohlayman — kichik ekranlarda ham barcha elementlar qulay joylashgan bo'lsin.

#### Qabul mezonlari

1. THE Ilova SHALL barcha sahifalarni mobile-first yondashuv bilan qursin — asosiy breakpoint 375px dan boshlansin
2. THE Ilova SHALL touch-friendly elementlar ishlatsin — barcha interaktiv elementlar kamida 44x44px touch target hajmiga ega bo'lsin
3. THE Ilova SHALL safe-area-inset qiymatlarini hisobga olsin — notch va pastki navigation bar ustiga kontent chiqmasin
4. THE Ilova SHALL font o'lchamlarini mobil qurilmalar uchun optimallashtirilsin — asosiy matn 14-16px, sarlavhalar 18-24px
5. THE Ilova SHALL gorizontal scroll paydo bo'lishiga yo'l qo'ymasin — barcha kontentlar ekran kengligiga moslashsin (overflow-x: hidden)
6. THE Ilova SHALL formalar va input maydonlarida mobil klaviatura ochilganda kontent siljishini to'g'ri boshqarsin

---

### Talab 21: Sprint tahrirlash funksiyasi

**User Story:** Men (tashkilotchi) sifatida, DRAFT holatdagi sprintimni tahrirlashni xohlayman, shunda parametrlarni to'g'rilash mumkin.

#### Qabul mezonlari

1. WHEN tashkilotchi DRAFT statusidagi sprintning "Tahrirlash" tugmasini bossa, THE Ilova SHALL tahrirlash formasini sprint ma'lumotlari bilan to'ldirilgan holda ko'rsatsin
2. THE Ilova SHALL barcha yaratish formasi maydonlarini tahrirlash imkonini bersin — sarlavha, tavsif, mukofot fondi, g'oliblar soni, sanalar va topshiriqlar
3. WHEN "Saqlash" tugmasi bosilganda, THE Ilova SHALL PUT /api/events/:id endpointiga yangilangan ma'lumotlarni yuborsin
4. IF sprint statusi "DRAFT" dan farqli bo'lsa, THEN THE Ilova SHALL tahrirlash imkonini bermasin va "Sprint muzlatilgan, tahrirlash mumkin emas" xabarini ko'rsatsin
5. WHEN "To'lovga o'tkazish" tugmasi bosilganda, THE Ilova SHALL tasdiqlash modalini ko'rsatsin — "Sprint sozlamalari muzlatiladi va o'zgartirib bo'lmaydi. Davom etasizmi?" matni bilan

---

### Talab 22: Toast bildirishnoma tizimi

**User Story:** Men (foydalanuvchi) sifatida, amallar natijasi haqida qisqa va aniq bildirishnomalar olmoqchiman, shunda nima bo'lganini tushunaman.

#### Qabul mezonlari

1. THE Ilova SHALL global Toast boshqaruvchisini (toast manager) yaratsin — uiStore orqali toast-lar qo'shilsin va boshqarilsin
2. THE Ilova SHALL 4 turdagi Toast-ni qo'llab-quvvatlasin: success (yashil), error (qizil), warning (sariq), info (ko'k)
3. WHEN yangi toast qo'shilganda, THE Ilova SHALL uni ekranning pastki qismida slide-in animatsiyasi bilan ko'rsatsin
4. THE Ilova SHALL toast-ni 3 soniyadan keyin avtomatik yopilsin (auto-dismiss) — foydalanuvchi qo'lda ham yopishi mumkin
5. WHEN bir vaqtda bir nechta toast bo'lsa, THE Ilova SHALL ularni stack (ustma-ust) shaklida ko'rsatsin — maksimal 3 ta ko'rinuvchan

