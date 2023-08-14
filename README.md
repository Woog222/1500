## 실행 방법
> 가상환경 venv을 생성 후에 사용하기를 권장합니다. 모든 코드는 python3.10를 기반으로 작성되었습니다.

```bash
# create venv
python -m venv .venv

# activate venv
source .venv/Scripts/activate

# upgrade pip
python3 -m pip install --upgrade pip

# install requirements.txt
pip install -r requirements.txt # 원도우

```

## 전처리 돌리는 방식
### Raw data
`data/raw` 안에 아래 파일들 넣고 python main.py -r
- od_matrix.csv
- orders.csv
- terminals.csv
- vehicles.csv

전처리 된 파일 data 폴더에 txt 파일로 저장됨

### Processed data
`data` 안에 아래 파일들 넣고 python main.py
- od_matrix.txt
- orders.txt
- terminals.txt
- vehicles.txt
