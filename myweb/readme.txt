/myweb
├── myweb				# django 기본 app    
│   ├── _init__.py			
│   ├── asgi.py
│   ├── settings.py			# 설정 파일
│   ├── urls.py				# url 설정 파일
│   └── wsgl.py
├── media				
├── static				
│   ├── admin
│   ├── assets
│   ├── css				# 부트스트랩 적용을 위한 css 폴더
│   ├── └── styles.css
│   ├── images				# html에 넣을 이미지들
│   ├── js				# 자바스크립트 파일
│   └── wsgl.py
│
├── br					# 실제 웹서비스 구현을 위한 app
│   ├── migrations			# migrate log 
│   ├── predModel			# train된 모델들을 저장할 폴더
│   │   ├── twohand_lv0_A
│   │   ├── twohand_lv0_R
│   │   ├── twohand_lv0_V
│   │   ├── twohand_lv1_A
│   │   ├── twohand_lv1_R
│   │   ├── twohand_lv1_V
│   │   ├── twohand_lv2_A
│   │   ├── twohand_lv2_R
│   │   └── twohand_lv2_V
│   ├── templates			# 템플릿 저장 폴더
│   │   └── br
│   │	    ├── base.html
│   │       ├── dashboard.html
│   │       ├── exercise1.html
│   │       ├── exercise2.html
│   │       ├── exercise3.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── password.html
│   │       ├── register.html
│   │       └── temp.html
│   ├── _init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py	
│   ├── models.py			# model 생성 파일
│   ├── tests.py
│   ├── urls.py				# url 설정 파일
│   └── views.py			# 실제로 동작되는 함수들이 작성된 파일
│
├── accounts				# 회원가입, 로그인을 위한 app
│   ├── migrations			# migrate log
│   ├── templates			# 템플릿 저장 폴더
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py			# 회원가입, 로그인 form 구현을 위한 파일
│   ├── models.py			# model 생성 파일
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py				# url 설정 파일
│   └── views.py			# 실제로 동작되는 함수들이 작성된 파일
└── migrations
