# Python 데이터 워크플로 Rock 만들기

## 실습 2.1

이 디렉토리에서 `rockcraft.yaml`을 생성하세요.
```bash
rockcraft init
```

생성된 `rockcraft.yaml` 을 열고, 아래 값을 우선 수정 합니다.

- `name`: `python-workflow` 로 수정
- `base`: `ubuntu@24.04` 로 수정
- `version`: `0.1`로 지정
- `summary`: 컨테이너 이미지에 대한 간략한 설명으로 교체
- `description`: 컨테이너 이미지에 대한 자세한 설명으로 교체

이번 실습에서는 컨테이너에 SQL Server 드라이버를 함께 포함해야 하는데, 해당 드라이버를 제공해는 패키지는 우분투 Main 저장소에서 제공되지 않습니다. 따라서 `package-repositories` 속성을 통해 Microsoft 에서 제공하는 패키지 저장소를 추가로 사용하도록 설정합니다.

`platforms`, `parts` 속성 사이에, `package-repositories` 속성을 추가하고. 아래와 같이 하위 값을 넣어 Microsoft 에서 제공하는 우분투 패키지 저장소를 추가로 사용하도록 설정합니다. 각 속성을 설명하면 아래와 같습니다.

- `type`: 패키지 저장소 유형 입니다. Ubuntu/Debian 패키지 저장소 (APT 저장소)이므로 `apt`로 지정 합니다.
- `url`: 패키지 저장소 서버 주소 입니다.
- `components`: 저장소에서 이용할 패키지 모음 유형입니다.
- `suites`: 어떤 우분투 릴리즈(버전)용으로 만들어진 패키지를 이용할지 지정합니다. 24.04 LTS 용 패키지를 이용하므로 `noble`로 지정 하였습니다.
- `key-id`: 패키지 저장소에서 저장소 메타데이터 및 패키지 서명에 사용하는 PGP키의 ID(16자리) 혹은 핑거프린트
- `key-server`: `key-id`에 해당하는 PGP키를 불러올 수 있는 URL
- `priority`: 패키지 저장소 사용 우선 순위 

```yaml
platforms: # the platforms this rock should be built on and run on
    amd64:

package-repositories:
    - type: apt
      url: https://packages.microsoft.com/ubuntu/24.04/prod
      components: [main]
      suites: [noble]
      key-id: BC528686B50D79E339D3721CEB3E94ADBE1229CF
      key-server: https://packages.microsoft.com/keys/microsoft.asc
      priority: always


parts:
    ...
```

빌드 과정을 정의 해 보겠습니다. `parts` 에서 빌드 과정을 정의 합니다. 이번에는 `workflow-deps` 및 `workflow` 두 가지 `parts`를 아래와 같은 형태로 작성 시작 해 봅시다.
```yaml
...
parts:
    workflow-deps:
        ...
    workflow:
        ...
...
```
`workflow-deps` part에는 아래와 같은 속성을 지정 해 줍니다.
- `plugin`: `python` 플러그인으로 지정 합니다.
- `source-type`: `local` 로 지정 합니다.
- `source`: `.` - 현재 디렉토리로 지정 합니다.
- `build-packages`: 두 가지 패키지를 빌드 단계에서 쓸 패키지로 넣어 줍니다. 실제로는 `msodbcsql18` 설치도 필요한데, 이 패키지는 설치 시 환경변수 `ACCEPT_EULA=Y` 전달이 필요하나, `build-packages` 속성으로 전달이 불가 하므로, `override-build`를 대신 활용 할 것입니다.
```yaml
build-packages:
    - python3-venv
    - unixodbc-dev
```
- `stage-packages`: 두 가지 패키지를 빌드 단계에서 쓸 패키지로 넣어 줍니다.
```yaml
stage-packages:
    - python3-venv
    - msodbcsql18
    - libgssapi-krb5-2
```
- `python-requirements`: Python 패키지 의존성 목록이 정의된 requirements.txt 파일 위치를 넣어 줍니다.
```yaml
python-requirements:
   - requirements.txt
```
- `override-build`: 앞서 설치하지 못한 `msodbcsql18`를 먼저 설치하고, 나머지 플러그인 등이 지정한 명령을 실행 하도록 `craftctl default`를 넣어 줍니다. 이후 ODBC 설치 구성도 빌드 단계에서 설치 영역에 생성 되도록 명령줄을 추가 합니다.
```yaml
override-build: |
    ACCEPT_EULA=y apt install -y msodbcsql18
    craftctl default
    ODBCINI=$CRAFT_PART_INSTALL/etc/odbcinst.ini ODBCSYSINI=$CRAFT_PART_INSTALL/etc odbcinst -i -d -f /opt/microsoft/msodbcsql18/etc/odbcinst.ini 
```

`workflow` part는 아래와 같이 작성 합니다.
- `plugin`: `dump` - 단순히 소스 파일을 Staging 영역에 복사 해 주는 플러그인 입니다.
- `organize`: 빌드 영역의 파일을 Staging 영역에서는 어떻게 정리할 지 지정하는 구성 입니다. 여기서는 `*.py` 파일을 Staging 영역에 넣을 때 `/root/`에 넣도록 하였습니다.
```yaml
...
workflow:
    source: .
    plugin: dump
    organize:
        '*.py': root/
...
```

Rock 을 빌드 해 보겠습니다. 아래 명령을 실행합니다.
```bash
rockcraft pack
```

빌드된 `*.rock` 파일을 Docker 에 이미지로 불러옵니다.
```bash
sudo rockcraft.skopeo --insecure-policy copy oci-archive:python-workflow_0.1_amd64.rock docker-daemon:python-workflow:0.1
```

아래와 같은 명령을 실행하여 워크플로가 잘 실행 되는지 확인 합니다.
```bash
export SRC_URL="https://raw.githubusercontent.com/canonical/rockcraft/refs/heads/main/schema/rockcraft.json"
export USERNAME=<구분 가능한 임의의 사용자명으로 수정>
export DB_CONN_STR='DRIVER={ODBC Driver 18 for SQL Server};SERVER=<DB서버 주소>;DATABASE=<접속할 DB이름>;UID=<DB계정 사용자명>;PWD=<DB계정 암호>'
sudo docker run python-workflow:0.1 exec python3 main.py --src-url $SRC_URL --inserted-by $USERNAME --dest-sqlserver-connstr "${DB_CONN_STR}"
```

아래와 같은 로그가 출력 된다면, 빌드한 Rock이 잘 작동하는 것 입니다. `rockcraft.yaml` 작성이 어렵다면, 완성된 예제 파일인 `rockcraft-solution-2.1.yaml`을 확인 해 보시기 바랍니다.

```bash
https://raw.githubusercontent.com/canonical/rockcraft/refs/heads/main/schema/rockcraft.json
youngbinhan
Connecting to SQL Server.
Inserting ETL Data.
Inserted ETL Data ID : 2
ETL Data inserted!
```

## 실습 2.2

앞서 생성한 `rockcraft.yaml` 파일은 임의로 이름을 수정(예: `rockcraft-ex-1.1.yaml`)하여 백업하고, 새로운 `rockcraft.yaml`을 생성하세요.
```bash
rockcraft init
```

생성된 `rockcraft.yaml` 을 열고, 아래 값을 우선 수정 합니다.

- `name`: `python-workflow` 로 수정
- `base`: `bare` 로 수정
- `build-base`: `ubuntu@24.04` 로 수정
- `version`: `0.2`로 지정
- `summary`: 컨테이너 이미지에 대한 간략한 설명으로 교체
- `description`: 컨테이너 이미지에 대한 자세한 설명으로 교체

이번 실습에서는 컨테이너에 SQL Server 드라이버를 함께 포함해야 하는데, 해당 드라이버를 제공해는 패키지는 우분투 Main 저장소에서 제공되지 않습니다. 따라서 `package-repositories` 속성을 통해 Microsoft 에서 제공하는 패키지 저장소를 추가로 사용하도록 설정합니다.

`platforms`, `parts` 속성 사이에, `package-repositories` 속성을 추가하고. 아래와 같이 하위 값을 넣어 Microsoft 에서 제공하는 우분투 패키지 저장소를 추가로 사용하도록 설정합니다. 각 속성을 설명하면 아래와 같습니다.

- `type`: 패키지 저장소 유형 입니다. Ubuntu/Debian 패키지 저장소 (APT 저장소)이므로 `apt`로 지정 합니다.
- `url`: 패키지 저장소 서버 주소 입니다.
- `components`: 저장소에서 이용할 패키지 모음 유형입니다.
- `suites`: 어떤 우분투 릴리즈(버전)용으로 만들어진 패키지를 이용할지 지정합니다. 24.04 LTS 용 패키지를 이용하므로 `noble`로 지정 하였습니다.
- `key-id`: 패키지 저장소에서 저장소 메타데이터 및 패키지 서명에 사용하는 PGP키의 ID(16자리) 혹은 핑거프린트
- `key-server`: `key-id`에 해당하는 PGP키를 불러올 수 있는 URL
- `priority`: 패키지 저장소 사용 우선 순위 

```yaml
platforms: # the platforms this rock should be built on and run on
    amd64:

package-repositories:
    - type: apt
      url: https://packages.microsoft.com/ubuntu/24.04/prod
      components: [main]
      suites: [noble]
      key-id: BC528686B50D79E339D3721CEB3E94ADBE1229CF
      key-server: https://packages.microsoft.com/keys/microsoft.asc
      priority: always


parts:
    ...
```

빌드 과정을 정의 해 보겠습니다. `parts` 에서 빌드 과정을 정의 합니다. 이번에는 `workflow-deps` 및 `workflow` 두 가지 `parts`를 아래와 같은 형태로 작성 시작 해 봅시다.
```yaml
...
parts:
    workflow-deps:
        ...
    workflow:
        ...
...
```

`workflow-deps` part에는 아래와 같은 속성을 지정 해 줍니다.
- `plugin`: `python` 플러그인으로 지정 합니다.
- `source-type`: `local` 로 지정 합니다.
- `source`: `.` - 현재 디렉토리로 지정 합니다.
- `build-packages`: 두 가지 패키지를 빌드 단계에서 쓸 패키지로 넣어 줍니다. 실제로는 `msodbcsql18` 설치도 필요한데, 이 패키지는 설치 시 환경변수 `ACCEPT_EULA=Y` 전달이 필요하나, `build-packages` 속성으로 전달이 불가 하므로, `override-build`를 대신 활용 할 것입니다.
```yaml
build-packages:
    - python3-venv
    - unixodbc-dev
```

- `stage-package` 에는 `msodbcsql18`, `python3.12-venv`, `libgssapi-krb5-2` 를 포함해야 합니다. 아래와 같은 몇가지 문제가 있습니다. 때문에 이번에 `stage-package`에는 `msodbcsql18`만 포함하고, `python3.12-venv`, `libgssapi-krb5-2`는 Chisel Slice 를 확인하여 `override-build` 단계에서 `chisel` 명령으로 직접 설치 진행 되도록 해 보겠습니다.
    - `stage-packages` 에 Slice 된 패키지 이름과 일반 패키지를 섞을 수 없습니다. (예: 일반 패키지인 `msodbcsql18` 및 Chisel 처리된 패키지 Slice 인 `aspnetcore-runtime-8.0_libs` 를 동시에 포함 불가)
    - 현재 Chisel 에서 Ubuntu Archive 에서 제공하는 패키지 이외 서드파티 (Third Party) 제공 패키지에 대한 Chiseling 은 지원하지 않습니다. (Slice 구성 직접 정의 해도 사용 불가)

```yaml
stage-packages:
    - msodbcsql18
```
- `python-requirements`: Python 패키지 의존성 목록이 정의된 requirements.txt 파일 위치를 넣어 줍니다.
```yaml
python-requirements:
   - requirements.txt
```

- `override-build`: 
  - 앞서 `build-packages` 에서 설치하지 못한 `msodbcsql18`를 먼저 설치하고
  - 이후 ODBC 설치 구성도 빌드 단계에서 설치 영역에 생성 되도록 명령줄을 추가 합니다.
  - Chisel Slice 설치 명령줄(`chisel cut`)도 넣어 줍니다. (Slice 이름 조회하여 수정하는 것은 다음 단계에서 진행합니다.)
  - 나머지 플러그인 등이 지정한 명령을 실행 하도록 `craftctl default`를 넣어 줍니다. 
```yaml
override-build: |
    ACCEPT_EULA=y apt install -y msodbcsql18
    chisel cut --root ${CRAFT_PART_INSTALL} <Chisel Slice 이름 나열>
    ODBCINI=$CRAFT_PART_INSTALL/etc/odbcinst.ini ODBCSYSINI=$CRAFT_PART_INSTALL/etc odbcinst -i -d -f /opt/microsoft/msodbcsql18/etc/odbcinst.ini 
    craftctl default
```

`chisel cut` 명령줄에 전달할 패키지인 `python3.12-venv`, `libgssapi-krb5-2` 에 대해 Chisel Slice 정보를 확인 해 봅니다.

```bash
chisel info python3.12-venv libgssapi-krb5-2
```

아래와 같이 Chisel Slice 정보가 조회 됩니다. 
```bash
2024/11/08 14:43:22 Consulting release repository...
2024/11/08 14:43:23 Cached ubuntu-24.04 release is still up-to-date.
2024/11/08 14:43:23 Processing ubuntu-24.04 release...
package: python3.12-venv
archive: ubuntu
slices:
    copyright:
        contents:
            /usr/share/doc/python3.12-venv: {symlink: /usr/share/doc/python3.12}
    ensurepip:
        essential:
            - python3.12-venv_copyright
            - python3-pip-whl_wheels
            - python3-setuptools-whl_wheels
            - python3.12_standard
        contents:
            /usr/lib/python3.12/ensurepip/*.py: {}
---
package: libgssapi-krb5-2
archive: ubuntu
slices:
    copyright:
        contents:
            /usr/share/doc/libgssapi-krb5-2/copyright: {}
    libs:
        essential:
            - libgssapi-krb5-2_copyright
            - libc6_libs
            - libcom-err2_libs
            - libk5crypto3_libs
            - libkrb5-3_libs
            - libkrb5support0_libs
        contents:
            /usr/lib/*-linux-*/libgssapi_krb5.so.2*: {}
```

출력된 결과를 참고하여, `python3.12-venv` 에 대해서는 `ensurepip`, `libgssapi-krb5-2`에 대해서는 `libs` Slice 를 설치 하도록 수정 해 보겠습니다. 그러면 `override-build`를 아래와 같이 수정이 가능합니다.
```yaml
override-build: |
    ACCEPT_EULA=y apt install -y msodbcsql18
    chisel cut --root ${CRAFT_PART_INSTALL} python3.12-venv_ensurepip libgssapi-krb5-2_libs # 수정된 명령줄
    ODBCINI=$CRAFT_PART_INSTALL/etc/odbcinst.ini ODBCSYSINI=$CRAFT_PART_INSTALL/etc odbcinst -i -d -f /opt/microsoft/msodbcsql18/etc/odbcinst.ini 
    craftctl default
```

`workflow` part는 아래와 같이 작성 합니다.
- `plugin`: `dump` - 단순히 소스 파일을 Staging 영역에 복사 해 주는 플러그인 입니다.
```yaml
...
workflow:
    source: .
    plugin: dump
...
```

이번에는 환경변수도 컨테이너 이미지에 추가로 설정 해 줍니다. `base`가 `bare`여서 이미지 베이스가 정말 아무것도 없는 것이기 때문에, 일반적으로 시스템에 포함되는 환경변수도 없는 경우가 있어 설정이 필요합니다. 이번 실습에서는 `PYTHONPATH`를 설정 해 주겠습니다. 아래와 같이 `parts`, `name`등과 같은 최상위 단계 속성으로 `environment` 속성을 추가하고 아래와 같이 지정 하여 requirements.txt 에서 설치한 Python 패키지를 정상적으로 컨테이너 내부에서 불러올 수 있도록 합니다.

```yaml

package-repositories:
    ...

environment:
    PYTHONPATH: /usr/lib/python3.12/site-packages

parts:
    workflow-deps:
        ...
    workflow:
        ...
```

Rock 을 빌드 해 보겠습니다. 아래 명령을 실행합니다.
```bash
rockcraft pack
```
빌드된 `*.rock` 파일을 Docker 에 이미지로 불러옵니다.
```bash
sudo rockcraft.skopeo --insecure-policy copy oci-archive:python-workflow_0.2_amd64.rock docker-daemon:python-workflow:0.2
```

아래와 같은 명령을 실행하여 워크플로가 잘 실행 되는지 확인 합니다.
```bash
export SRC_URL="https://raw.githubusercontent.com/canonical/rockcraft/refs/heads/main/schema/rockcraft.json"
export USERNAME=<구분 가능한 임의의 사용자명으로 수정>
export DB_CONN_STR='DRIVER={ODBC Driver 18 for SQL Server};SERVER=<DB서버 주소>;DATABASE=<접속할 DB이름>;UID=<DB계정 사용자명>;PWD=<DB계정 암호>'
sudo docker run python-workflow:0.1 exec python3 main.py --src-url $SRC_URL --inserted-by $USERNAME --dest-sqlserver-connstr "${DB_CONN_STR}"
```

아래와 같은 로그가 출력 된다면, 빌드한 Rock이 잘 작동하는 것 입니다. `rockcraft.yaml` 작성이 어렵다면, 완성된 예제 파일인 `rockcraft-solution-2.2.yaml`을 확인 해 보시기 바랍니다.

```bash
https://raw.githubusercontent.com/canonical/rockcraft/refs/heads/main/schema/rockcraft.json
youngbinhan
Connecting to SQL Server.
Inserting ETL Data.
Inserted ETL Data ID : 2
ETL Data inserted!
```

## 두 컨테이너 비교하기

컨테이너 이미지 크기와 이미지에 포함된 파일 구성을 비교 해 보겠습니다.

먼저 `docker images` 명령으로, 이미지 크기를 비교 해 봅니다. 0.1이 실습 1.1에서 플러그인 및 Chisel 사용 없이 빌드 한 것, 0.2가 실습 1.2 에서 플러그인과 Chisel 및 bare base 사용하여 빌드한 것 입니다.
```bash
$ sudo docker images
REPOSITORY       TAG       IMAGE ID       CREATED          SIZE
python-workflow   0.2       8c867c7046dd   54 minutes ago   157MB
python-workflow   0.1       eb75f2ffdcc9   2 weeks ago      222MB
```

컨테이너 이미지에 포함된 파일을 비고 해 보겠습니다. 이미지에서 실행한 컨테이너 목록을 조회하고, 각 컨테이너를 `tar` 파일로 내보내기한 후 비교 해 봅니다.

먼저 `docker ps -a`로 컨테이너를 조회하고, `docker export <컨테이너 이름> > <원하는 파일명>.tar` 로 내보내기 합니다.

```bash
$ sudo docker ps -a
CONTAINER ID   IMAGE                COMMAND                  CREATED             STATUS                         PORTS     NAMES
3913939e3e8c   python-workflow:0.2   "/usr/bin/pebble ent…"   48 minutes ago      Exited (0) 42 minutes ago                gifted_williams
b9f7d3b048e1   python-workflow:0.1   "/usr/bin/pebble ent…"   25 hours ago        Exited (0) 22 hours ago                  jolly_satoshi
...
```

```bash
sudo docker export gifted_williams >  python-workflow-0.2.tar
sudo docker export jolly_satoshi > python-workflow-0.1.tar
```

아래 명령으로 `tar`파일 내부 파일 목록을 확인 합니다.
```bash
tar -tf python-workflow-0.2.tar
tar -tf python-workflow-0.1.tar
```