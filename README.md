# rockcraft-workshop

Rockcraft Workshop 실습 자료입니다.

## 실습 자료
- [실습1 - .NET Web API 앱 Rock 만들기](./dotnet-webapi/README.md)
- [실습2 - Python 데이터 워크플로 Rock 만들기](./python-workflow/README.md)

## 워크샵 참여 전 준비사항

Ubuntu 22.04 LTS, 24.04 LTS 혹은 그 이후 버전의 시스템에 Snap, LXD, Rockcraft, Chisel 을 미리 설치 한 후, 이 저장소를 로컬에 복제 해 두시기 바랍니다.

### Ubuntu 가 설치 된 장비
아래와 같은 방법 중 편한 방법으로 Ubuntu 22.04 LTS 혹은 24.04 LTS 이후 버전이 설치 된 장비를 준비 해 주시면 됩니다. 준비된 환경에서 Systemd 및 AppArmor 가 정상 작동해야 합니다. (이어서 설치할 Snap, LXD, Rockcraft, Chiselrk 정상적으로 설치되고 작동하면 실습에 이상 없는 환경으로 보시면 됩니다.)

- Ubuntu 가 설치 된 데스크톱이나 노트북
- Windows 설치된 데스크톱/노트북의 경우 WSL2 환경, Multipass로 초기화된 Ubuntu VM, Hyper-V 등 다른 VM 에 설치된 Ubuntu 환경 중 편한 방법으로 준비
- macOS 환경의 경우, Multipass 활용 권장. Parallels 혹은 UTM 등도 활용 가능.
- 퍼블릭 클라우드(AWS, Azure, Google Cloud 등)에서 Ubuntu VM 생성.

### LXD 사전 설치 (아래 명령줄 실행)
```bash
sudo snap install lxd
lxd init --auto
```
### Docker, Rockcraft, Chisel 사전 설치 (아래 명령줄 실행)
```
sudo snap install docker
sudo snap install rockcraft --classic
sudo snap install chisel
```
### LXD, Docker 네트워크 충돌 이슈
Docker와 충돌로 인해 LXD 네트워크 이슈 있는 경우, 아래 링크 참고하여 미리 설정 권장

https://documentation.ubuntu.com/lxd/en/latest/howto/network_bridge_firewalld/#prevent-connectivity-issues-with-lxd-and-docker 

### 워크샵 GitHub 저장소 로컬에 복제 해 두기
```bash
git clone https://github.com/ahnlabcloudmatelabs/rockcraft-workshop 
```