export const motivationalQuotes = [
  "Başarı, küçük çabaların günlük tekrarıdır.",
  "En iyi hazırlık bugünü en iyi şekilde kullanmaktır.",
  "Hedefleriniz büyük, adımlarınız küçük olsun.",
  "Başarı tesadüf değil, kararlılıktır.",
  "Bugün yapabileceklerini yarına bırakma.",
  "Odaklan, çalış, başar.",
  "Her gün biraz daha iyisi için çalış.",
  "Motivasyonun seni başlatmasına, alışkanlığın devam ettirmesine izin ver.",
  "Zamanın en değerli varlığındır, onu akıllıca kullan.",
  "Küçük ilerlemeler de ilerlemedir.",
  "Yapabildiğini yap, sahip olduğunla, olduğun yerde.",
  "Başarı, hazırlık ile fırsatın buluşmasıdır.",
  "Hedefe giden yolda her adım önemlidir.",
  "Bugün kendine yatırım yap.",
  "Erteleme, zamanın hırsızıdır.",
  "Konsantre ol, azimli ol, başarılı ol.",
  "En zor adım ilk adımdır, atla!",
  "Verimlilik, işleri doğru yapmaktır. Etkililik, doğru işleri yapmaktır.",
  "Zamanı yönetemezsin, sadece kendini yönetebilirsin.",
  "Her pomodoro bir adım daha yaklaştırır seni hedefe."
];

export const getRandomQuote = () => {
  return motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];
};

export default { motivationalQuotes, getRandomQuote };
