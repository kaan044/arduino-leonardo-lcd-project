#include <LiquidCrystal.h>

// DOĞRULANMIŞ BAĞLANTI AYARIN:
// RS->12, E->11, D4->5, D5->4, D6->3, D7->2
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600); // Python ile haberleşme hızı
  lcd.begin(16, 2);
  
  // Açılış Ekranı
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Sistem");
  lcd.setCursor(0, 1);
  lcd.print("Bekleniyor...");
}

void loop() {
  // Python'dan veri gelmesini bekle

  if (Serial.available() > 0) {
    // Satır sonuna kadar oku (Örn: "CPU:50C GPU:60C;RAM: %48\n")
    String data = Serial.readStringUntil('\n');
    
    // Veriyi noktalı virgülden (;) ikiye böl
    int ayirici = data.indexOf(';');
    
    if (ayirici > 0) {
      String satir1 = data.substring(0, ayirici);      // Üst Satır
      String satir2 = data.substring(ayirici + 1);     // Alt Satır
      
      // 1. Satırı Yaz
      lcd.setCursor(0, 0);
      lcd.print(satir1);
      // Eğer gelen veri kısa kalırsa, satırın geri kalanını boşlukla temizle
      for(int i = satir1.length(); i < 16; i++) { lcd.print(" "); }
      
      // 2. Satırı Yaz
      lcd.setCursor(0, 1);
      lcd.print(satir2);
      // Alt satırı da temizle
      for(int i = satir2.length(); i < 16; i++) { lcd.print(" "); }
    }
  }
}