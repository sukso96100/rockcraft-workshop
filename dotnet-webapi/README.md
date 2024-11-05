# .NET Web API 앱 Rock 만들기

## 실습 1.1

이 디렉토리에서 `rockcraft.yaml`을 생성하세요.
```bash
rockcraft init
```

생성된 `rockcraft.yaml` 을 열고, 아래 값을 우선 수정 합니다.

- `name`: `weather-webapi` 로 수정
- `base`: `ubuntu@24.04` 로 수정
- `summary`: 컨테이너 이미지에 대한 간략한 설명으로 교체
- `description`: 컨테이너 이미지에 대한 자세한 설명으로 교체

빌드 과정을 정의 해 보겠습니다. `parts` 에서 빌드 과정을 정의 합니다. `my-part` 를 `weather-webapi`로 바꾸고 하위 속성을 아래와 같이 추가하여 빌드 과정을 정의 합니다.

- `source-type`: 빌드에 사용할 소스 유형을 지정합니다. `local` 로 지정해 주세요.
- `source`: 소스 위치 지정. 현재 디렉토리로 지정하기 위해 `.` 으로 입력합니다.
- `build-environment`: 빌드 단계에서 사용할 환경변수 입니다. `PATH` 환경변수 지정을 위해 배열 항목으로 `PATH: "/usr/bin:${PATH}"`를 넣어줍니다.
- `build-packages`: 빌드 환경에서 필요한 우분투 패키지 입니다. .NET 빌드에 필요한 패키지인 `dotnet-sdk-8.0`를 배열 항목으로 넣어줍니다.
- `stage-packages`: 완성된 컨테이너에 포함되어 앱 실행시 필요한 우분투 패키지 입니다. .NET 런타임 패키지인 `aspnetcore-runtime-8.0`를 배열 항목으로 넣어줍니다.
- `override-build`: 빌드 과정에서 실행할 명령어를 재정의 합니다. 아래와 같이 수정합니다.
```yaml
override-build: |
    craftctl default
    dotnet restore
    dotnet build 
    dotnet publish -c Release -o ${CRAFT_PART_INSTALL}/
```

`plarform` 및 `parts` 사이에 아래 내용을 추가하여 컨테이너 환경변수와 내부에서 실행할 서비스 구성을 정의 합니다. 여기서 정의한 `services` 의 경우 추후 컨테이너 내부에서 [`pebble`](https://canonical-pebble.readthedocs-hosted.com/en/latest/) 에 의해 실행 됩니다. 

```yaml
environment:
    ASPNETCORE_URLS: http://0.0.0.0:8080

services:
    weather-webapi:
        override: replace
        startup: enabled
        command: dotnet rockcraft-workshop.dll
```

Rock 을 빌드 해 보겠습니다. 아래 명령을 실행합니다.
```bash
rockcraft pack
```

빌드된 `*.rock` 파일을 Docker 에 이미지로 불러옵니다.
```bash
sudo rockcraft.skopeo --insecure-policy copy oci-archive:weather-webapi_0.1_amd64.rock docker-daemon:weather-webapi:0.1
```

컨테이너를 로컬에서 실행하고, `http://localhost:8080/weatherforecast` 에 접속하여 잘 작동하는지 확인 해 봅니다.
```bash
sudo docker run -p 8080:8080 weather-webapi:0.1
```

JSON 데이터가 잘 반환 된다면, 빌드한 Rock이 잘 작동하는 것 입니다. `rockcraft.yaml` 작성이 어렵다면, 완성된 예제 파일인 `rockcraft-solution-1.1`을 확인 해 보시기 바랍니다.