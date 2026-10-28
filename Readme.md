# ConTeXt AdvancedKit — قالب با پوشه‌های تگ

هر بخش، فایل‌های مشترک و شرط‌های خودش را نگه می‌دارد. **فایل در پوشهٔ مادر مشترک است؛ فایل داخل زیرپوشهٔ تگ فقط برای همان شرط است.** فارسی و انگلیسی هر دو صریح‌اند: `fa` فارسی است و `en` انگلیسی. فایل انگلیسی را به‌عنوان فایل مشترک قرار ندهید.

## شروع سریع

Python 3.10+ و ConTeXt LMTX لازم است. دستورها از هر مسیری قابل اجرا هستند؛ ریشهٔ پیش‌فرض، محل خود اسکریپت است.

```sh
python3 Generate-Outputs.py --target fa-screen
python3 Generate-Outputs.py --target en-printed --watch
python3 Generate-Outputs.py
```

دستور آخر چهار خروجی `en-screen`، `en-printed`، `fa-screen` و `fa-printed` را می‌سازد. PDF در `Outputs/advanced-fa-screen.pdf` و گزارش در `.build/fa-screen/compile.log` قرار می‌گیرد. شکست کامپایل، PDF موفق قبلی را جایگزین نمی‌کند. برای توقف رصد `Ctrl+C` بزنید.

## کدام فایل را ویرایش کنم؟

| مسیر واقعی | مسئولیت |
| --- | --- |
| `main.ctx` | ورودی مشترک و ترتیب بارگذاری تنظیمات و محتوا |
| `section/ContentLayout.ctx` | ترتیب مشترک فصل‌ها برای هر دو زبان |
| `section/en/` | متن انگلیسی: پیش‌گفتار، فصل و پایان |
| `section/fa/` | متن فارسی با همان نام فایل‌ها |
| `setups/*.ctx` | تنظیمات مشترک: ساختار صفحه، کاور، ماکروها و fallback |
| `setups/en/` | زبان، جهت، نام‌های انگلیسی و فونت پایهٔ انگلیسی |
| `setups/fa/` | زبان، جهت، نام‌های فارسی و فونت پایهٔ فارسی |
| `setups/en-printed/FontsDef.ctx` | فونت انگلیسی مخصوص چاپ |
| `setups/fa-printed/FontsDef.ctx` | فونت فارسی مخصوص چاپ |
| `setups/screen/Theme.ctx` | رنگ‌های خروجی نمایشگر، مشترک بین دو زبان |
| `setups/printed/Theme.ctx` | رنگ‌های خروجی چاپ، مشترک بین دو زبان |
| `setups/s4/Size.ctx` و `setups/a5/Size.ctx` | اندازهٔ صفحه، مستقل از زبان و تم |
| `sources/` | منابع: فونت، تصویر، نماد و کتاب‌نامه |
| `sources/FontCollection/en/` | فونت‌های انگلیسی و مجوزهای همراه |
| `sources/FontCollection/fa/` | فونت‌های فارسی و مجوزهای همراه |
| `sources/FontCollection/Emoji_font/` | فونت ایموجی مشترک |
| `project.json` | بخش‌های پروژه، دسته‌های تگ و خروجی‌ها |
| `tools/` | انتخاب فایل، آماده‌سازی، کامپایل و رصد |

`section`، `setups` و `sources` هرکدام بخش مستقلی هستند. پوشه‌ای به نام `common` لازم نیست؛ خود پوشهٔ مادر محل فایل‌های مشترک است. لازم نیست همهٔ بخش‌ها همهٔ تگ‌ها را داشته باشند: مثلاً `section` تفاوت اندازهٔ صفحه ندارد و پوشهٔ `a5` در آن نساخته‌ایم.

برای افزودن فصل، نام آن را در `section/ContentLayout.ctx` وارد کنید. اگر متن مشترک است، آن را در `section/new-chapter.ctx` بگذارید؛ اگر ترجمه دارد، دو فایل `section/fa/new-chapter.ctx` و `section/en/new-chapter.ctx` بسازید. افزودن فایل به پوشه به‌تنهایی آن را به ترتیب فصل‌ها اضافه نمی‌کند.

## پوشه‌های تگ چگونه کار می‌کنند؟

تگ‌ها در `project.json` ثبت می‌شوند. دسته‌های نمونه `language`، `theme` و `size` هستند. هر انتخاب حداکثر یک تگ از هر دسته دارد. شناسهٔ تگ، حرف کوچک لاتین، عدد و زیرخط دارد و در پروژه یکتا است.

**فقط نام کامل یک زیرپوشه تگ است**؛ نام فایل‌ها تغییر نمی‌کند. ترکیب چند تگ با خط تیره در نام پوشه ممکن است. پوشهٔ تگ از مسیر منطقی حذف می‌شود و شرط آن به همهٔ فرزندان می‌رسد.

| فایل واقعی | مسیر منطقی در کامپایل | شرط |
| --- | --- | --- |
| `section/intro.ctx` | `section/intro.ctx` | مشترک |
| `section/en/intro.ctx` | `section/intro.ctx` | `en` |
| `section/fa/intro.ctx` | `section/intro.ctx` | `fa` |
| `setups/fa/FontsDef.ctx` | `setups/FontsDef.ctx` | `fa` |
| `setups/fa-printed/FontsDef.ctx` | `setups/FontsDef.ctx` | هم `fa` و هم `printed` |
| `setups/a5/Size.ctx` | `setups/Size.ctx` | `a5` |
| `sources/Images/fa/map.svg` | `sources/Images/map.svg` | `fa`؛ شرط محلی بخش تصاویر |

نام‌های عادی مثل `Lang-Vars.ctx`، `intro-fa.ctx` یا پوشهٔ `notes-fa` به تگ تفسیر نمی‌شوند. برای شرط فارسی، فایل را داخل `fa/` قرار دهید. شرط‌ها در همهٔ بخش‌ها یک منطق دارند و شرط بخش همسایه به بخش دیگر سرایت نمی‌کند.

1. همهٔ تگ‌های شرط یک فایل باید فعال باشند (AND).
2. نسخه با بیشترین تعداد تگ منطبق انتخاب می‌شود؛ مثلاً `fa-printed` از `fa` مشخص‌تر است.
3. فایل بدون تگ، نسخهٔ مشترکِ جایگزین است؛ همراه نسخهٔ منتخب دوباره بارگذاری نمی‌شود.
4. دو نسخهٔ دارای بالاترین رتبهٔ برابر خطا می‌دهند؛ نسخهٔ ترکیبی بسازید یا شرط‌ها را اصلاح کنید.
5. فایلی که فقط نسخهٔ زبانی دارد در انتخاب بدون آن زبان حضور ندارد؛ انگلیسی به‌طور ضمنی جای فارسی نمی‌نشیند.

می‌توانید شرط‌های ارثی مثل `setups/fa/printed/FontsDef.ctx` هم داشته باشید؛ شرط آن با `setups/fa-printed/FontsDef.ctx` یکسان است. برای ساختار کم‌عمق، در نمونه از نام ترکیبی استفاده شده است. دو شکل را برای یک فایل هم‌زمان نسازید؛ هم‌رتبه‌اند و تعارض دارند. تکرار یک تگ رتبهٔ بیشتری ایجاد نمی‌کند.

## افزودن بخش یا خروجی

بخش‌های فعال در `components` ثبت شده‌اند:

```json
"components": ["section", "setups", "sources"]
```

اگر پوشه‌ای مثل `writing` یا `template` دارید، نامش را به همین فهرست اضافه کنید. سپس `writing/intro.ctx` مشترک و `writing/fa/intro.ctx` فارسی خواهد بود؛ نیازی به تغییر اسکریپت پایتون نیست. فقط بخش‌های ثبت‌شده وارد انتخاب و رصد می‌شوند. نام بخش، شناسهٔ سادهٔ کوچک و متفاوت از نام تگ است.

برای افزودن نسخهٔ مدرس، دسته و خروجی زیر را به JSON موجود اضافه کنید؛ بقیهٔ تنظیمات را حفظ کنید:

```json
{
  "tag_categories": {"edition": ["teacher", "student"]},
  "targets": {"fa-teacher": ["fa", "screen", "s4", "teacher"]}
}
```

`section/teacher/section1.ctx` مخصوص مدرس است. اگر نسخهٔ `section/fa/section1.ctx` هم وجود داشته باشد، برای انتخاب فارسیِ مدرس، `section/fa-teacher/section1.ctx` را بسازید تا دو شرط هم‌رتبه تعارض نداشته باشند.

ترکیب زبان، تم و اندازه مستقل است؛ برای نمونه می‌توانید فارسیِ نمایشگر با اندازهٔ A5 بسازید:

```sh
python3 Generate-Outputs.py --tags fa,screen,a5
python3 Generate-LoadPath.py --tags fa,screen,a5
python3 Generate-Outputs.py --target fa-screen --list
python3 Generate-Outputs.py --target fa-screen --prepare
```

`Generate-LoadPath.py` فقط نسخهٔ منتخب و `PathList.ctx` را آماده می‌کند. برای کامپایل مستقیم، وارد `.build/fa-screen/` شوید و `context main.ctx` را اجرا کنید. همهٔ پوشه‌های تگ را مستقیماً به مسیر جست‌وجوی TeX اضافه نکنید؛ فقط فایل‌های منتخب باید دیده شوند.

`--list` نگاشت مسیر منطقی به فایل واقعی را نشان می‌دهد. `.build/<target>/selection.json` نیز همین نگاشت و تگ‌ها را نگه می‌دارد. `--target` تکرارپذیر است و با `--tags` ترکیب نمی‌شود. برای پروژه‌ای دیگر از `--root /path/to/project` استفاده کنید. در نمونهٔ حاضر، ترکیب دلخواه باید زبان، تم و اندازه را مشخص کند تا فایل‌های ضروری موجود باشند.

## رصد تغییرات

`--watch` فایل‌های منتخب و تنظیمات خروجی را رصد می‌کند. ویرایش، افزودن، حذف و تغییر نام در چرخهٔ بعدی دیده می‌شود؛ تغییر فارسی، خروجی انگلیسی را دوباره نمی‌سازد. تغییر فایل مشترک همهٔ خروجی‌های استفاده‌کننده را متأثر می‌کند. بازهٔ پیش‌فرض نیم‌ثانیه است و با `--interval 1` تغییر می‌کند. پس از شکست کامپایل، اصلاح منبع موجب تلاش مجدد می‌شود.

`.build`، `Outputs`، پوشه‌های مخفی، `Backups` و کش پایتون ورودی نیستند. symlink در منابع پشتیبانی نمی‌شود. نام فایل‌های TeX، فونت و تصویر در مجموعهٔ منتخب باید یکتا باشد، چون قالب آن‌ها را با نام فایل فراخوانی می‌کند؛ برخورد نام با خطا متوقف می‌شود.

## مهاجرت

| مسیر قبلی | مسیر فعلی |
| --- | --- |
| `section/preface.ctx` با متن انگلیسی | `section/en/preface.ctx` |
| `section-fa/preface.ctx` | `section/fa/preface.ctx` |
| `setups/Direction.ctx` با جهت انگلیسی | `setups/en/Direction.ctx` |
| `setups/Direction-fa.ctx` | `setups/fa/Direction.ctx` |
| `setups/FontsDef-fa-printed.ctx` | `setups/fa-printed/FontsDef.ctx` |
| `setups/FontsDef-printed.ctx` | `setups/en-printed/FontsDef.ctx` |
| `setups/Theme.ctx` و `Theme-printed.ctx` | `setups/screen/Theme.ctx` و `setups/printed/Theme.ctx` |
| `setups/Size.ctx` و `Size-a5.ctx` | `setups/s4/Size.ctx` و `setups/a5/Size.ctx` |
| `Common-Setups/` و `Common-Sources/` در نسخه‌های قدیمی‌تر | فایل‌های مشترک در `setups/` و `sources/` |
| `En/Common-Sections/` و `Fa/Common-Sections/` | `section/en/` و `section/fa/` |

پوشهٔ همسایهٔ قدیمی مثل `section-fa` با خطای راهنمای انتقال رد می‌شود. پسوند تگ در نام فایل دیگر شرط نیست؛ آن را به زیرپوشهٔ تگ منتقل کنید. `main.ctx` و نام‌های ورودی آن ثابت‌اند. `.build` تولیدی است و با اجرای اسکریپت بازسازی می‌شود.

محتوا، تنظیمات حروف‌چینی، فونت‌ها و مجوزها حفظ شده‌اند؛ فونت‌های هر زبان فقط برای همان زبان آماده می‌شوند. `sources/Images/diagram1.png` همچنان placeholder متنی است و پیش از استفاده باید با تصویر واقعی جایگزین شود.

## آزمون و مجوز

```sh
python3 -m unittest discover -s tests -v
```

آزمون‌ها انتخاب زبان، فایل مشترک، شرط ترکیبی، تعارض، بخش‌های سفارشی، منابع، رصد و حفظ PDF قبلی هنگام شکست را بررسی می‌کنند. آزمون واحد جای کامپایل و بررسی بصری PDF برای فارسی و ایموجی را نمی‌گیرد.

کد پروژه تحت MIT است؛ مجوز فونت‌ها و سایر منابع مستقل است. مجوزهای همراه را حفظ کنید.
