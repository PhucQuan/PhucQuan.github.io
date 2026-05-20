
### I. Giới thiệu tổng quan về K8S

![](/assets/images/posts/Pasted%20image%2020260520094943.png)

Trong các hệ thống hiện đại, ứng dụng thường không còn được triển khai dưới dạng một khối duy nhất trên một máy chủ cố định. Thay vào đó, chúng được chia nhỏ thành nhiều service, đóng gói dưới dạng container và chạy trên nhiều máy chủ khác nhau. Cách tiếp cận này giúp ứng dụng dễ triển khai, dễ mở rộng và linh hoạt hơn, nhưng đồng thời cũng tạo ra một bài toán mới: làm thế nào để quản lý hàng chục, hàng trăm hoặc thậm chí hàng nghìn container một cách ổn định?

Kubernetes, thường được viết tắt là K8s, là một nền tảng mã nguồn mở dùng để điều phối container. Nó giúp tự động hóa các công việc như triển khai ứng dụng, phân bổ tài nguyên, mở rộng số lượng instance, cân bằng tải, tự phục hồi khi container gặp lỗi và quản lý vòng đời của workload trong môi trường phân tán.

Kubernetes trở nên phổ biến vì nó giải quyết được nhiều vấn đề cốt lõi khi vận hành ứng dụng container hóa ở quy mô lớn. Thay vì phải tự chọn máy chủ để chạy container, tự restart khi lỗi, tự cấu hình load balancing hoặc tự scale thủ công, người vận hành chỉ cần khai báo trạng thái mong muốn của hệ thống. Kubernetes sẽ chịu trách nhiệm đưa trạng thái thực tế của cluster về gần nhất với trạng thái đã khai báo.

So với việc chạy container thủ công bằng Docker trên từng máy chủ riêng lẻ, Kubernetes cung cấp một lớp điều phối mạnh hơn nhiều. Nó không chỉ chạy container, mà còn quản lý scheduling, networking, service discovery, storage, secret, rollout/rollback và khả năng tự phục hồi. Đây là lý do Kubernetes trở thành nền tảng tiêu chuẩn trong nhiều hệ thống cloud-native, microservices, DevOps và CI/CD hiện nay.

Tầm quan trọng của Kubernetes không chỉ nằm ở khả năng vận hành ứng dụng, mà còn nằm ở việc nó trở thành lớp hạ tầng trung tâm của nhiều hệ thống hiện đại. Một cluster Kubernetes có thể chứa nhiều ứng dụng quan trọng, dữ liệu nhạy cảm, thông tin xác thực, service nội bộ và quyền truy cập tới hạ tầng bên dưới. Vì vậy, nếu Kubernetes bị cấu hình sai hoặc bị tấn công, hậu quả có thể không chỉ dừng lại ở một container riêng lẻ mà có thể ảnh hưởng tới toàn bộ cluster.

Chính vì vậy, để nghiên cứu các kỹ thuật tấn công và leo thang đặc quyền trong Kubernetes, trước tiên cần hiểu rõ kiến trúc và vai trò của từng thành phần trong cluster. Đây là nền tảng để phân tích attacker có thể xâm nhập từ đâu, lạm dụng quyền như thế nào và cần áp dụng các cơ chế phòng thủ nào để bảo vệ hệ thống.

## II. Tìm hiểu về kiến trúc K8S

Kubernetes là một hệ thống điều phối container mã nguồn mở được sử dụng rộng rãi ,giúp giảm tải công việc khi tự động triển khai ,thu phóng hoặc quản lý container trong các hệ thống phân tán . 

Về ý tưởng thì K8S tạo ra 1 platform để chạy các container trên các máy chủ (Baremental hoặc VM ) mà việc cấp pháp và quản lý tài nguyên do K8S đảm nhiệm 

![](/assets/images/posts/Pasted%20image%2020260517212337.png)


Như hình ảnh bạn thấy ở trên thì một Kubernetes sẽ bao gồm 2 phần chính là **Control Plane** và **Worker Nodes** . Control Plane đóng vai trò là bộ não của cluster , chịu trách nhiệm quản lý , điều phối và duy trì trạng thái mong muốn của hệ thống . Cùng vào đó thì các Worker nodes chịu trách nhiệm là nơi cùng cấp tài nguyên cho các ứng dụng container hóa dưới dạng Pods.

![](/assets/images/posts/Pasted%20image%2020260520094140.png)

## II. Các thành phần trong Control Plane 

![](/assets/images/posts/Pasted%20image%2020260520094014.png)

Sau khi hiểu tổng quan rằng một Kubernetes cluster gồm **Control Plane** và **Worker Nodes**, ta sẽ đi sâu hơn vào từng thành phần bên trong. Mỗi thành phần có một vai trò riêng, nhưng chúng phối hợp với nhau để đảm bảo ứng dụng luôn chạy đúng trạng thái mong muốn.

###  Control plane 

Control Plane nói đơn giản như nó là 1 trung tâm điều khiển của K8S cluster . Nó không trực tiếp chạy ứng dụng mà chịu trực tiếp quản lí toàn bộ trạng thái của cluster , đưa ra quyết định và phản ứng khi có sự cố xảy ra . 

Ví dụ, khi bạn tạo một Deployment với 3 replicas, Control Plane sẽ đảm bảo luôn có 3 Pods đang chạy. Nếu một Pod bị lỗi hoặc một Node gặp sự cố, Control Plane sẽ phát hiện và yêu cầu tạo Pod mới ở nơi phù hợp.


#### Các thành phần chính của Control Plane bao gồm 

### 1. API Server

`kube-apiserver` là thành phần trung tâm của Kubernetes Control Plane. Nếu xem Kubernetes cluster như một hệ thống phân tán gồm nhiều thành phần khác nhau, thì API Server chính là **cổng giao tiếp chính** để tất cả các thành phần đó làm việc với nhau.

Mọi thao tác với Kubernetes gần như đều đi qua API Server. Khi người dùng chạy `kubectl`, khi dashboard gửi request, khi CI/CD pipeline deploy ứng dụng, hoặc khi các component nội bộ như scheduler, controller-manager, kubelet cần cập nhật trạng thái, tất cả đều giao tiếp thông qua Kubernetes API.

Có thể hiểu đơn giản:

> `kube-apiserver` là entry point của Kubernetes cluster. Nó tiếp nhận request, kiểm tra request có hợp lệ và có được phép thực hiện hay không, sau đó ghi nhận trạng thái mới vào `etcd`.

Một điểm quan trọng là API Server **không tự chạy container** và cũng **không tự quyết định Pod chạy ở Node nào**. Nó đóng vai trò như lớp trung gian điều phối request và lưu trạng thái. Các thành phần khác sẽ quan sát trạng thái trong cluster thông qua API Server rồi thực hiện nhiệm vụ của mình.

Ví dụ, khi ta chạy lệnh:

```bash
kubectl apply -f nginx-deployment.yaml
```

Luồng xử lý ở mức high level sẽ như sau:

```text
kubectl gửi request đến kube-apiserver
        ↓
kube-apiserver xác thực danh tính người gửi request
        ↓
kube-apiserver kiểm tra người đó có quyền thực hiện hành động hay không
        ↓
Admission Controller kiểm tra hoặc chỉnh sửa object trước khi lưu
        ↓
kube-apiserver ghi trạng thái mong muốn vào etcd
        ↓
Các component khác như scheduler/controller/kubelet quan sát thay đổi này
        ↓
Cluster dần đưa trạng thái thực tế về đúng trạng thái mong muốn
```


![](/assets/images/posts/Pasted%20image%2020260520090705.png)

Hình ảnh minh họa : https://iximiuz.com/en/posts/kubernetes-api-how-to-extend/

#### API Server xử lý request như thế nào?

Một request gửi tới Kubernetes API Server thường đi qua các bước quan trọng sau:

**1. Authentication - xác thực danh tính**

API Server cần biết request này đến từ ai. Danh tính đó có thể là user, admin, service account, hoặc một component nội bộ trong cluster.

Một số cơ chế authentication phổ biến gồm:

- X.509 client certificate
- Bearer token
- ServiceAccount token
- OIDC token
- Webhook token authentication

Ví dụ, khi một Pod gọi đến API Server, nó thường sử dụng ServiceAccount token được mount vào trong Pod tại đường dẫn:

```text
/var/run/secrets/kubernetes.io/serviceaccount/token
```

Đây cũng là lý do trong các kịch bản tấn công Kubernetes, sau khi attacker có shell trong Pod, một trong những việc đầu tiên họ thường làm là kiểm tra token này.

**2. Authorization - kiểm tra quyền**

Sau khi biết request đến từ ai, API Server cần kiểm tra người đó có được phép thực hiện hành động hay không.

Trong Kubernetes, cơ chế authorization phổ biến nhất là **RBAC**.

Ví dụ:

- User A có được `get pods` trong namespace `default` không?
- ServiceAccount B có được `create pods` không?
- ServiceAccount C có được `get secrets` không?
- Một account có được `create clusterrolebindings` hay không?

Các câu hỏi này được trả lời thông qua RBAC rules.

Một lệnh thường dùng để kiểm tra quyền là:

```bash
kubectl auth can-i get pods
```

Hoặc kiểm tra quyền của một ServiceAccount cụ thể:

```bash
kubectl auth can-i --list --as=system:serviceaccount:attack-lab:vulnerable-sa
```

Trong privilege escalation, phần RBAC rất quan trọng vì nhiều attack path bắt đầu từ một ServiceAccount có quyền quá rộng. Ví dụ nếu một ServiceAccount có quyền `create pods`, `get secrets`, `bind`, `escalate`, `impersonate` hoặc wildcard `*`, attacker có thể lạm dụng để leo thang đặc quyền.

**3. Admission Control - kiểm tra trước khi object được lưu**

Sau authentication và authorization, request còn có thể đi qua Admission Controller.

Admission Controller là lớp kiểm soát cuối cùng trước khi object được lưu vào etcd. Nó có thể:

- Cho phép request
- Từ chối request
- Tự động thêm/sửa một số field trong object

Ví dụ, trong bài toán security, Admission Controller có thể được dùng để chặn các Pod nguy hiểm như:

- Pod chạy với `privileged: true`
- Pod dùng `hostPath` để mount filesystem của Node
- Pod bật `hostPID`, `hostIPC`, `hostNetwork`
- Container cho phép `allowPrivilegeEscalation: true`
- Container chạy bằng user root

Các công cụ như **Pod Security Admission**, **Kyverno** hoặc **OPA Gatekeeper** đều hoạt động ở lớp này để enforce policy.

**4. Persist state vào etcd**

Nếu request vượt qua các bước kiểm tra, API Server sẽ ghi trạng thái mới vào `etcd`.

Điểm cần nhớ là Kubernetes vận hành theo mô hình **desired state**. Người dùng khai báo trạng thái mong muốn, API Server lưu trạng thái đó vào etcd, sau đó các component khác sẽ dần đưa hệ thống về đúng trạng thái mong muốn.

Ví dụ, khi ta tạo Deployment với 3 replicas, thông tin “tôi muốn có 3 Pod” được lưu vào etcd. Sau đó controller-manager, scheduler và kubelet phối hợp để tạo và chạy các Pod tương ứng.

#### API Server trong cluster local

Nếu cluster được dựng bằng `kubeadm`, `kind` hoặc `minikube`, `kube-apiserver` thường chạy dưới dạng Pod trong namespace `kube-system`.

Có thể kiểm tra bằng lệnh:

```bash
kubectl get pods -n kube-system
```

Hoặc lọc riêng API Server:

```bash
kubectl get pods -n kube-system -o name | grep apiserver
```

Trong mô hình kubeadm, manifest của API Server thường nằm tại:

```text
/etc/kubernetes/manifests/kube-apiserver.yaml
```

Đây là static Pod manifest. Khi file manifest này thay đổi, kubelet trên control plane node sẽ tự động phát hiện và restart static Pod tương ứng.

#### Góc nhìn bảo mật

API Server là một trong những attack surface quan trọng nhất của Kubernetes. Nếu API Server bị expose sai cách, cấu hình authentication/authorization yếu, hoặc RBAC quá rộng, attacker có thể enumerate tài nguyên, đọc secret, tạo workload độc hại hoặc leo thang lên quyền cao hơn.

Một số rủi ro thường gặp:

- Bật anonymous access không kiểm soát
- RBAC cấp quyền quá rộng cho user hoặc ServiceAccount
- Không bật audit log nên khó điều tra hành vi bất thường
- Admission policy không chặn được Pod nguy hiểm
- API Server bị expose ra Internet hoặc mạng không tin cậy
- Token/kubeconfig bị lộ, cho phép attacker gọi API Server như người dùng hợp lệ

Một số hướng hardening quan trọng:

- Bật RBAC và áp dụng nguyên tắc least privilege
- Hạn chế quyền nguy hiểm như `create pods`, `get secrets`, `bind`, `escalate`, `impersonate`, `create clusterrolebindings`
- Bật Kubernetes audit log để ghi nhận các hành vi nhạy cảm
- Dùng Pod Security Admission hoặc Kyverno để chặn Pod nguy hiểm
- Không expose API Server ra ngoài nếu không cần thiết
- Bảo vệ kubeconfig, ServiceAccount token và certificate
- Xoay vòng credential khi nghi ngờ bị lộ


### 2. ETCD

`etcd` là nơi lưu trữ toàn bộ dữ liệu trạng thái cluster dưới dạng key-value store

Các thông tin như Nodes , Pods, Services, Config Maps , Secrets, Deployment,... đều được lưu trong etcd.

Ví dụ , khi bạn tạo một Deployment , thông tin về Deployment đó sẽ được lưu vào etcd. Sau đó các thành phần khác của Control Planel sẽ đọc trạng thái này và thực hiện các hoạt động cần thiết để biến trạng thái mong muốn thành thực tế . Mọi thông tin khi bạn sử dụng lệnh `kubectl` để truy xuất đều từ etcd data store.

Vì etcd lưu dữ liệu quan trọng của cluster , nên nó thường cần có cơ chế backup trong môi trường production.

Tùy thuộc và cách bạn setup cluster , etcd thì setup theo kiểu khác. Bạn có thể setup etcd from scatch sử dụng binary hoặc có thể deploy etcd bằng cách sử dụng kubeadm,minikube,k3s tools, . Dưới đây là case mà etcd được deploy dưới dạng Pod nằm trong kubesystem namspace .

Xem etcd pod

![](/assets/images/posts/Pasted%20image%2020260519212052.png)


Lưu etcd pod name trong biến môi trường

![697](/assets/images/posts/Pasted%20image%2020260519212147.png)

Xem rõ hơn về thông tin về Pod để biết được thiết lập ở trong etcd datastore 

```
kubectl describe pod $ETCDPODNAME -n kube-system
```


![](/assets/images/posts/Pasted%20image%2020260519212333.png)

Nhìn vào output của pod etcd ở trên, ta có thể thấy etcd đang chạy trong namespace `kube-system` với tên pod là `etcd-control-plane-o3n9bb2t`. Phần quan trọng cần chú ý là cấu hình `--advertise-client-urls`.


Đây chính là endpoint mà etcd dùng để lắng nghe kết nối từ Kubernetes API Server. Port 2379 là port mặc định dành cho client của etcd. Vì vậy, khi kiểm tra cấu hình của API Server, flag --etcd-servers cũng sẽ trỏ tới cùng địa chỉ này.

Ta có thể lưu endpoint này vào biến môi trường để sử dụng ở các bước tiếp theo:

![](/assets/images/posts/Pasted%20image%2020260519213239.png)

Sau khi chạy lệnh echo, nếu terminal in ra đúng giá trị https://172.31.3.83:2379 thì biến môi trường đã được thiết lập thành công.


Tiếp theo , chúng ta biết etcd sử dụng dạng lưu trữ key:value vậy nên chúng ta cũng có thể liệt kê được các key lưu trữ sau bằng cách chạy dòng lệnh này 

![](/assets/images/posts/Pasted%20image%2020260519213450.png)

 Root path trong etcd chính thường được sử dụng là `/registry`. Bên dưới `/registry`, Kubernetes lưu nhiều loại tài nguyên khác nhau như `pods`, `replicasets`, `deployments`, `services`, `secrets`, `configmaps`, v.v.


Lấy thông tin chi tiết về Pod

![](/assets/images/posts/Pasted%20image%2020260519214717.png)

#### Vì sao etcd nhạy cảm?

`etcd` rất nhạy cảm vì nó lưu toàn bộ trạng thái cluster. Nếu attacker đọc được etcd, họ có thể thu thập nhiều thông tin quan trọng như:

- Secret của ứng dụng
- Token hoặc credential được lưu trong Secret
- Cấu hình hệ thống
- Danh sách ServiceAccount
- RBAC rules
- Thông tin về workload, namespace và service nội bộ

Đặc biệt, Kubernetes Secret không phải là cơ chế mã hóa mạnh theo mặc định ở tầng object. Secret thường được biểu diễn dưới dạng base64 trong manifest. Base64 chỉ là encoding, không phải encryption.

Trong production, để bảo vệ Secret trong etcd, cần bật **encryption at rest** cho Kubernetes Secret. Khi đó dữ liệu Secret trước khi lưu vào etcd sẽ được mã hóa bằng encryption provider phù hợp.

Nói chính xác hơn:

> Kubernetes Secret được encode base64 khi biểu diễn dưới dạng YAML/JSON. Việc Secret có được mã hóa khi lưu trong etcd hay không phụ thuộc vào cấu hình encryption at rest của cluster.

#### etcd và attack path

Trong một số kịch bản tấn công, attacker có thể nhắm tới etcd theo các hướng sau:

- etcd port `2379` bị expose ra network không tin cậy
- etcd không yêu cầu TLS client certificate đúng cách
- attacker chiếm được control plane node và đọc được certificate của etcd
- attacker tạo privileged pod hoặc hostPath pod để đọc filesystem trên control plane node
- attacker có quyền exec vào etcd pod trong namespace `kube-system`

Nếu attacker đọc được etcd trực tiếp, họ có thể bỏ qua API Server và RBAC. Đây là worst case vì các lớp kiểm soát như authentication, authorization, admission control không còn phát huy tác dụng ở đường truy cập trực tiếp này.

Một số hướng hardening quan trọng:

- Không expose etcd ra Internet hoặc mạng không tin cậy
- Chỉ cho API Server và thành phần cần thiết truy cập etcd
- Bật TLS cho etcd client/server communication
- Bật encryption at rest cho Kubernetes Secret
- Phân quyền chặt chẽ trên control plane node
- Bảo vệ certificate tại `/etc/kubernetes/pki/etcd/`
- Mã hóa và kiểm soát truy cập backup etcd
- Theo dõi log và network connection bất thường tới port `2379`

#### Backup và khôi phục etcd

Vì etcd lưu toàn bộ trạng thái cluster, backup etcd là một phần rất quan trọng trong vận hành Kubernetes production.

Nếu etcd bị mất dữ liệu hoặc corrupt, cluster có thể mất trạng thái về workload, service, secret, RBAC và nhiều object khác. Vì vậy, production cluster thường cần:

- Backup etcd định kỳ
- Kiểm tra khả năng restore từ backup
- Bảo vệ file backup vì backup cũng có thể chứa Secret
- Mã hóa backup và giới hạn quyền truy cập backup

Điểm dễ bị bỏ qua là: **backup etcd cũng nhạy cảm gần như etcd thật**. Nếu attacker lấy được backup, họ có thể phân tích offline để tìm secret, token và cấu hình quan trọng.


Trong  privilege escalation, etcd có thể được trình bày như một mục tiêu có giá trị cao. Attack path chính của mình không nhất thiết phải demo chiếm etcd trực tiếp, nhưng cần giải thích rõ rằng nếu attacker có thể truy cập etcd hoặc đọc backup etcd, họ có thể thu thập dữ liệu cực kỳ nhạy cảm và làm suy yếu toàn bộ cluster.


### 3. Scheduler

Scheduler không trực tiếp chạy container và cũng không tạo container. Nhiệm vụ chính của nó là **ra quyết định Pod nên được chạy trên Node nào**. Sau khi Scheduler chọn được Node phù hợp, thông tin này sẽ được cập nhật lại vào Pod object thông qua API Server. Lúc đó kubelet trên Node được chọn mới nhận nhiệm vụ thực sự chạy Pod.

Có thể hiểu đơn giản:

> kube-scheduler giống như bộ phận điều phối tài nguyên trong cluster. Nó nhìn vào yêu cầu của Pod và tình trạng của các Node, sau đó chọn nơi phù hợp nhất để đặt Pod.


Khi chọn Node cho Pod, Scheduler thường trải qua hai giai đoạn chính là **Filtering** và **Scoring**.

**Filtering** là bước loại bỏ các Node không đủ điều kiện để chạy Pod.

Ví dụ, nếu Pod yêu cầu 2 CPU nhưng một Node chỉ còn 1 CPU khả dụng thì Node đó sẽ bị loại. Tương tự, nếu Pod yêu cầu chạy trên Node có label cụ thể nhưng Node không có label đó thì Node cũng không được chọn.

Một số yếu tố thường được xem xét trong bước filtering gồm:

- CPU và memory còn trống trên Node
- `nodeSelector`
- Node affinity hoặc anti-affinity
- Taints và tolerations
- Volume binding
- Trạng thái Node có healthy hay không

**Scoring** là bước chấm điểm các Node còn lại sau khi đã filtering.

Sau khi loại bỏ các Node không phù hợp, Scheduler sẽ xếp hạng các Node còn lại. Node nào phù hợp hơn sẽ có điểm cao hơn. Ví dụ, Scheduler có thể ưu tiên Node còn nhiều tài nguyên hơn hoặc Node giúp phân tán Pod đều hơn trong cluster.

Cuối cùng, Node có điểm cao nhất sẽ được chọn để chạy Pod.

### Ví dụ kiểm tra Scheduler trong cluster

Tạo một Pod đơn giản:

```bash
kubectl run mypod --image=nginx
```

Kiểm tra Pod đang chạy trên Node nào:

```bash
kubectl get pod mypod -o wide
```

Kiểm tra Pod được schedule bởi scheduler nào:

```bash
kubectl get pod mypod -o jsonpath='{.spec.schedulerName}'
```

Thông thường kết quả sẽ là:

```text
default-scheduler
```

Xem chi tiết event của Pod:

```bash
kubectl describe pod mypod
```

Trong phần `Events`, ta có thể thấy thông tin Pod đã được schedule lên Node nào. Đây là cách dễ nhất để quan sát quá trình scheduling trong lab.

Nếu cluster được dựng bằng `kubeadm`, `kind` hoặc `minikube`, `kube-scheduler` thường chạy dưới dạng Pod trong namespace `kube-system`.

```bash
kubectl get pods -n kube-system | grep scheduler
```

Trong mô hình kubeadm, manifest của Scheduler thường nằm tại:

```text
/etc/kubernetes/manifests/kube-scheduler.yaml
```

Port mặc định của kube-scheduler là `10259`.

### Góc nhìn bảo mật

So với API Server, etcd hoặc kubelet, Scheduler thường không phải là attack surface trực tiếp phổ biến nhất. Tuy nhiên, scheduling vẫn liên quan đến bảo mật vì nó quyết định workload được đặt ở đâu trong cluster.

Một số rủi ro có thể xảy ra nếu attacker có quyền tạo hoặc chỉnh sửa Pod:

- Attacker có thể dùng `nodeSelector`, `nodeName`, affinity hoặc tolerations để ép Pod chạy trên một Node cụ thể.
- Nếu Pod được schedule lên Node nhạy cảm, attacker có thể tăng khả năng tiếp cận workload hoặc tài nguyên quan trọng trên Node đó.
- Nếu Pod được phép dùng cấu hình nguy hiểm như `hostPath`, `hostPID`, `hostNetwork` hoặc `privileged`, việc Pod được đặt lên Node quan trọng có thể dẫn tới rủi ro chiếm quyền trên Node.
- Nếu taints/tolerations cấu hình lỏng lẻo, workload không đáng tin cậy có thể chạy trên Node vốn dùng cho workload quan trọng.

Vì vậy, khi hardening Kubernetes, cần kết hợp scheduling control với các lớp bảo vệ khác:

- Hạn chế quyền tạo/sửa Pod bằng RBAC least privilege.
- Dùng Pod Security Admission hoặc Kyverno để chặn Pod nguy hiểm.
- Dùng taints/tolerations để cô lập Node quan trọng.
- Quản lý chặt quyền chỉnh sửa label của Node.
- Dùng NetworkPolicy để giảm rủi ro lateral movement sau khi Pod đã được schedule.


### 4. Controller

Kube Controller hay còn  được gọi là Controller manager là một thành phần thuộc Control Plane, chịu trách nhiệm chạy nhiều controller khác nhau bên trong Kubernetes.

Nếu API Server là nơi tiếp nhận request, etcd là nơi lưu trạng thái, Scheduler là nơi quyết định Pod chạy ở Node nào, thì Controller Manager là thành phần liên tục theo dõi trạng thái hiện tại của cluster và cố gắng đưa nó về đúng trạng thái mong muốn.

Có thể hiểu đơn giản:

> Controller Manager là cơ chế tự động sửa sai của Kubernetes. Nó liên tục so sánh trạng thái hiện tại với trạng thái mong muốn, nếu thấy lệch thì thực hiện hành động để đưa cluster về đúng trạng thái đã khai báo.

Ví dụ, khi ta tạo một Deployment với 3 replicas, trạng thái mong muốn là luôn có 3 Pod chạy. Nếu một Pod bị lỗi hoặc bị xóa, Deployment Controller sẽ phát hiện hiện tại chỉ còn 2 Pod, sau đó tạo thêm 1 Pod mới để quay lại đúng 3 replicas.

Quy trình hoạt động ở mức high level:

```text
User khai báo desired state
        ↓
kube-apiserver lưu desired state vào etcd
        ↓
Controller Manager quan sát trạng thái qua API Server
        ↓
Phát hiện actual state khác desired state
        ↓
Controller tạo/sửa/xóa object cần thiết
        ↓
Cluster dần quay về trạng thái mong muốn
```

Trong Kubernetes, controller không chỉ có một loại. `kube-controller-manager` thực chất chạy nhiều controller khác nhau, mỗi controller phụ trách một nhóm nhiệm vụ riêng.

Một số controller phổ biến gồm:

- **Node Controller**: theo dõi trạng thái Node, phát hiện Node bị down hoặc không phản hồi.
- **Deployment Controller**: đảm bảo số lượng Pod của Deployment đúng với số replicas đã khai báo.
- **ReplicaSet Controller**: duy trì số lượng Pod replica theo yêu cầu.
- **Job Controller**: quản lý các Job chạy một lần hoặc chạy đến khi hoàn thành.
- **EndpointSlice Controller**: cập nhật danh sách endpoint phía sau Service.
- **ServiceAccount Controller**: đảm bảo ServiceAccount mặc định tồn tại trong namespace.
- **Token Controller**: xử lý một số logic liên quan đến token/secret của ServiceAccount trong các cơ chế token nhất định.

Ví dụ thực tế:

```bash
kubectl create deployment nginx --image=nginx --replicas=3
```

Sau khi chạy lệnh trên, API Server lưu Deployment object vào etcd. Deployment Controller sẽ phát hiện có một Deployment mới cần 3 replicas, sau đó tạo ReplicaSet và các Pod tương ứng. Nếu sau đó ta xóa một Pod:

```bash
kubectl delete pod <pod-name>
```

Controller sẽ tự động tạo Pod mới để đảm bảo Deployment vẫn có đủ 3 replicas.

Nếu cluster được dựng bằng `kubeadm`, `kube-controller-manager` thường chạy dưới dạng static Pod trong namespace `kube-system`.

```bash
kubectl get pods -n kube-system | grep controller-manager
```

Manifest thường nằm tại:

```text
/etc/kubernetes/manifests/kube-controller-manager.yaml
```

Một số flag đáng chú ý của controller-manager:

```text
--service-account-private-key-file
--root-ca-file
--cluster-signing-cert-file
--cluster-signing-key-file
--use-service-account-credentials
```

Các flag này liên quan đến certificate, ServiceAccount token và credential mà controller sử dụng để giao tiếp với API Server.

#### Góc nhìn bảo mật

Controller Manager liên quan tới bảo mật vì nó có quyền tạo, sửa, xóa nhiều loại tài nguyên trong cluster. Nếu credential của controller-manager bị lộ hoặc component này bị compromise, attacker có thể tác động mạnh đến trạng thái cluster.

Một số rủi ro cần chú ý:

- Credential/certificate của controller-manager bị lộ trên control plane node.
- Controller chạy với quyền quá rộng hoặc dùng chung credential không cần thiết.
- ServiceAccount token signing key bị lộ, attacker có thể tạo token giả trong một số mô hình cấu hình nhất định.
- Custom controller/operator bên thứ ba được cài vào cluster nhưng dùng ServiceAccount có quyền quá rộng.

Trong thực tế, rủi ro thường gặp không chỉ nằm ở `kube-controller-manager` mặc định của Kubernetes mà còn nằm ở các **custom controller/operator**. Nhiều Helm chart hoặc operator được cài vào cluster với quyền rất cao, ví dụ quyền tạo Pod, đọc Secret hoặc quản lý tài nguyên trên toàn cluster. Nếu operator đó có lỗ hổng hoặc bị compromise, attacker có thể lợi dụng ServiceAccount của operator để leo thang đặc quyền.

Một số hướng hardening:

- Bảo vệ control plane node và thư mục chứa certificate/key.
- Bật `--use-service-account-credentials` để mỗi controller dùng credential riêng thay vì dùng một credential chung quá rộng.
- Kiểm tra RBAC của các controller/operator bên thứ ba.
- Không cài operator/Helm chart không rõ nguồn gốc vào cluster production.
- Dùng audit log để theo dõi các hành động bất thường như tạo ClusterRoleBinding, đọc Secret hàng loạt, tạo privileged Pod.

### cloud-controller-manager

`cloud-controller-manager` là thành phần dùng khi Kubernetes cluster tích hợp với hạ tầng cloud provider như AWS, Google Cloud, Azure hoặc OpenStack.

Trong các cluster chạy local bằng `kind`, `minikube` hoặc các môi trường on-premise đơn giản, có thể không cần `cloud-controller-manager`. Nhưng trong môi trường cloud, thành phần này giúp Kubernetes giao tiếp với hạ tầng bên ngoài.

Một số nhiệm vụ phổ biến của cloud-controller-manager:

- Tạo hoặc cập nhật Load Balancer trên cloud khi dùng Service type `LoadBalancer`.
- Kiểm tra trạng thái VM/Node từ cloud provider.
- Quản lý route mạng trong cloud.
- Gắn metadata hoặc thông tin cloud vào Node object.
- Tích hợp với storage hoặc network provider của cloud.

Ví dụ, khi ta tạo Service kiểu LoadBalancer:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
    - port: 80
      targetPort: 80
```

Trong môi trường cloud, cloud-controller-manager có thể gọi API của cloud provider để tạo một load balancer thật bên ngoài, sau đó cập nhật địa chỉ IP/DNS của load balancer vào Service object trong Kubernetes.

#### Góc nhìn bảo mật

cloud-controller-manager là cầu nối giữa Kubernetes và cloud provider, nên nếu cấu hình sai, rủi ro không chỉ nằm trong cluster mà có thể lan sang hạ tầng cloud.

Một số rủi ro cần chú ý:

- Credential cloud provider bị lộ.
- Service type `LoadBalancer` expose ứng dụng ra Internet ngoài ý muốn.
- Cloud IAM role cấp quyền quá rộng cho Kubernetes component.
- Attacker có quyền tạo Service có thể làm lộ workload nội bộ ra bên ngoài nếu không có policy kiểm soát.
- Metadata service của cloud có thể bị Pod truy cập nếu không được chặn, dẫn đến lộ cloud credential trong một số môi trường.

Một số hướng hardening:

- Áp dụng least privilege cho cloud IAM role dùng bởi cluster.
- Kiểm soát quyền tạo Service type `LoadBalancer`.
- Dùng policy/admission controller để chặn expose service nhạy cảm.
- Giới hạn network egress từ Pod tới cloud metadata endpoint nếu không cần.
- Theo dõi các thay đổi bất thường liên quan tới LoadBalancer, Ingress và public IP.

##  Worker Nodes

Nếu Control Plane là nơi quản lý và đưa ra quyết định, thì Worker Nodes là nơi thực sự chạy ứng dụng.

Mỗi Worker Node cung cấp tài nguyên như CPU, RAM, network và storage để chạy các Pod. Một cluster có thể có một hoặc nhiều Worker Node tùy vào quy mô hệ thống.

Trên mỗi Worker Node thường có các thành phần chính sau:

- `kubelet`
- `kube-proxy`
- Container Runtime
- CNI plugin hoặc thành phần networking khác

Có thể hiểu đơn giản:

> Control Plane quyết định cluster nên chạy gì, còn Worker Node là nơi biến quyết định đó thành container đang chạy thật.

![](/assets/images/posts/Pasted%20image%2020260520094809.png)


### 1. kubelet

`kubelet` là agent chạy trên mỗi Node trong Kubernetes cluster.

Nhiệm vụ chính của kubelet là nhận thông tin Pod được gán cho Node của nó, sau đó làm việc với container runtime để pull image, tạo container, mount volume và duy trì trạng thái của Pod.

Ví dụ, sau khi Scheduler quyết định Pod `nginx` nên chạy trên Node `worker-1`, kubelet trên `worker-1` sẽ nhận thông tin này thông qua API Server. Sau đó kubelet gọi container runtime như `containerd` để pull image `nginx` và chạy container.

Luồng xử lý cơ bản:

```text
Scheduler gán Pod vào Node
        ↓
kubelet trên Node đó phát hiện Pod mới
        ↓
kubelet gọi container runtime
        ↓
container runtime pull image và chạy container
        ↓
kubelet theo dõi trạng thái Pod/container
        ↓
kubelet report trạng thái về API Server
```

Một số nhiệm vụ quan trọng của kubelet:

- Đăng ký Node với Kubernetes cluster.
- Nhận PodSpec từ API Server.
- Đảm bảo container trong Pod chạy đúng như khai báo.
- Mount volume cho Pod.
- Chạy liveness probe, readiness probe, startup probe.
- Báo cáo trạng thái Node, Pod và container về API Server.
- Quản lý static Pod trên Node.

Nếu dùng kubeadm, kubelet thường chạy như một systemd service trên Node, không phải Pod bình thường.

Có thể kiểm tra kubelet bằng:

```bash
sudo systemctl status kubelet
```

Hoặc xem process:

```bash
ps aux | grep kubelet
```

Một số file cấu hình quan trọng:

```text
/etc/kubernetes/kubelet.conf
/var/lib/kubelet/config.yaml
```

File `kubelet.conf` chứa thông tin để kubelet xác thực với API Server. Kubelet thường giao tiếp với API Server bằng danh tính dạng:

```text
system:node:<node-name>
```

và thuộc group:

```text
system:nodes
```

![](/assets/images/posts/Pasted%20image%2020260519230338.png)


Một cấu hình rất quan trọng trong kubelet là authentication và authorization.

Ví dụ trong `/var/lib/kubelet/config.yaml`, cần chú ý các phần như:

![](/assets/images/posts/Pasted%20image%2020260519230403.png)

```yaml
authentication:
  anonymous:
    enabled: false

authorization:
  mode: Webhook
```

`anonymous.enabled: false` nghĩa là kubelet không chấp nhận request ẩn danh.

`authorization.mode: Webhook` nghĩa là kubelet sẽ hỏi API Server để kiểm tra request có được phép thực hiện hay không.

Không nên dùng:

```text
authorization.mode: AlwaysAllow
```

Vì nếu kubelet dùng `AlwaysAllow`, request tới kubelet có thể được chấp nhận mà không kiểm soát quyền đúng cách.

#### Static Pod

Một khái niệm quan trọng khi học kubelet là **static Pod**.

Static Pod là Pod được kubelet quản lý trực tiếp từ file manifest trên Node, thay vì được tạo thông qua API Server như Pod thông thường.

Trong mô hình kubeadm, các component của Control Plane như API Server, Scheduler, Controller Manager thường chạy dưới dạng static Pod. Manifest của chúng nằm trong:

```text
/etc/kubernetes/manifests/
```

Kubelet sẽ theo dõi thư mục này. Nếu có file manifest mới hoặc manifest bị sửa, kubelet sẽ tự động tạo hoặc restart static Pod tương ứng.

Đây là lý do khi chỉnh file:

```text
/etc/kubernetes/manifests/kube-apiserver.yaml
```

API Server có thể tự restart sau một khoảng thời gian ngắn.

#### Góc nhìn bảo mật

Kubelet là một attack surface rất quan trọng trong Kubernetes vì nó chạy trên từng Node và có khả năng tương tác trực tiếp với container, Pod, log, exec và filesystem liên quan tới workload.

Một số rủi ro phổ biến:

- Kubelet port `10250` bị expose ra mạng không tin cậy.
- Bật anonymous authentication.
- Dùng `authorization.mode: AlwaysAllow`.
- Attacker có quyền gọi kubelet API để đọc logs, exec vào container hoặc lấy thông tin Pod trên Node.
- Node bị compromise dẫn tới lộ kubelet credential trong `/etc/kubernetes/kubelet.conf`.
- Pod nguy hiểm dùng `hostPath` để đọc thư mục nhạy cảm của Node, bao gồm file kubelet hoặc kubeconfig.

Một số hướng hardening:

- Tắt anonymous authentication cho kubelet.
- Dùng authorization mode `Webhook`.
- Không expose kubelet port `10250` ra Internet hoặc mạng không tin cậy.
- Giới hạn network access tới kubelet chỉ từ control plane hoặc thành phần cần thiết.
- Kiểm soát RBAC liên quan tới `nodes/proxy`, `nodes/log`, `nodes/exec`.
- Chặn Pod dùng `hostPath`, `hostPID`, `hostNetwork`, `privileged` nếu không cần.
- Dùng audit log và runtime security tool như Falco để phát hiện hành vi bất thường trên Node.

Trong đề tài privilege escalation, kubelet rất đáng chú ý vì nhiều attack path từ Pod có thể dẫn tới Node compromise nếu attacker tạo được privileged Pod hoặc mount được host filesystem.


### 2. kube-proxy

`kube-proxy` là thành phần networking chạy trên các Node để hỗ trợ Kubernetes Service.

Trong Kubernetes, Pod có IP riêng nhưng Pod có thể bị xóa và tạo lại liên tục, dẫn tới IP thay đổi. Vì vậy, Kubernetes dùng Service để cung cấp một địa chỉ ổn định cho nhóm Pod phía sau.

`kube-proxy` giúp triển khai cơ chế chuyển tiếp traffic từ Service tới Pod backend phù hợp.

Ví dụ, ta có một Service `frontend-service` trỏ tới 3 Pod frontend. Khi client gửi request tới Service, traffic sẽ được chuyển tới một trong các Pod backend. Các rule chuyển tiếp này có thể được kube-proxy cấu hình bằng `iptables` hoặc `IPVS`.

Có thể kiểm tra kube-proxy trong cluster:

```bash
kubectl get pods -n kube-system | grep kube-proxy
```

Vì kube-proxy thường chạy trên mọi Node, nó thường được triển khai dưới dạng DaemonSet:

```bash
kubectl get daemonset -n kube-system | grep kube-proxy
```

Xem log kube-proxy:

```bash
kubectl logs -l k8s-app=kube-proxy -n kube-system
```

Một số mode hoạt động phổ biến:

- **iptables mode**: phổ biến, dùng iptables rule để điều hướng traffic.
- **IPVS mode**: phù hợp với cluster lớn, cần hiệu năng network cao hơn.

#### Góc nhìn bảo mật

kube-proxy liên quan tới network traffic trong cluster. Bản thân kube-proxy không phải lúc nào cũng là mục tiêu tấn công trực tiếp, nhưng network model của Kubernetes có ảnh hưởng lớn đến lateral movement.

Mặc định, trong nhiều cluster, các Pod có thể giao tiếp với nhau khá tự do nếu không có NetworkPolicy. Điều này có nghĩa là nếu attacker compromise một Pod, họ có thể scan hoặc truy cập các Service nội bộ khác trong cluster.

Một số rủi ro:

- Không có NetworkPolicy, dẫn tới Pod-to-Pod traffic quá mở.
- Service expose nhầm workload nhạy cảm.
- NodePort hoặc LoadBalancer expose dịch vụ ra ngoài không kiểm soát.
- hostNetwork Pod có thể bypass một số lớp network isolation.
- Lạm dụng Service/Endpoint để điều hướng hoặc chặn traffic trong một số cấu hình sai.

Một số hướng hardening:

- Áp dụng NetworkPolicy theo hướng default deny.
- Chỉ expose Service ra ngoài khi thật sự cần.
- Kiểm soát quyền tạo Service type `NodePort` và `LoadBalancer`.
- Theo dõi traffic bất thường giữa các namespace.
- Tách namespace và network zone cho workload có mức độ nhạy cảm khác nhau.

### 3. Container Runtime

Container Runtime là thành phần thực sự chạy container trên Worker Node.

Kubernetes không tự chạy container trực tiếp. Thay vào đó, kubelet giao tiếp với container runtime thông qua chuẩn **CRI - Container Runtime Interface**.

Một số container runtime phổ biến:

- `containerd`
- `CRI-O`
- Các runtime tương thích CRI khác

Trước đây Docker từng được dùng phổ biến trong Kubernetes, nhưng các phiên bản Kubernetes hiện đại giao tiếp với runtime qua CRI, trong đó `containerd` là lựa chọn rất phổ biến.

Luồng xử lý cơ bản:

```text
kubelet nhận PodSpec
        ↓
kubelet gọi container runtime qua CRI
        ↓
runtime pull image
        ↓
runtime tạo container
        ↓
runtime quản lý lifecycle của container
```

Container runtime chịu trách nhiệm các việc như:

- Pull image từ registry.
- Tạo container filesystem.
- Khởi chạy process chính trong container.
- Quản lý container lifecycle.
- Kết nối container với network namespace phù hợp.
- Ghi nhận container log.

#### Góc nhìn bảo mật

Container Runtime là lớp rất quan trọng trong các kịch bản container escape hoặc node compromise.

Một số rủi ro phổ biến:

- Container chạy với `privileged: true`.
- Container được mount socket runtime như `containerd.sock` hoặc `docker.sock`.
- Container có Linux capability nguy hiểm như `SYS_ADMIN`.
- Container chạy bằng user root.
- Image chứa vulnerability hoặc tool nguy hiểm.
- Runtime hoặc kernel có lỗ hổng cho phép container escape.

Ví dụ, nếu một Pod được mount Docker socket hoặc container runtime socket, attacker có shell trong Pod có thể tương tác với runtime trên host và tạo container mới với quyền cao hơn. Đây là một dạng misconfiguration rất nguy hiểm.

Một số hướng hardening:

- Không mount runtime socket vào Pod.
- Hạn chế `privileged: true`.
- Drop Linux capabilities không cần thiết.
- Dùng `runAsNonRoot`, `readOnlyRootFilesystem` nếu phù hợp.
- Scan image bằng Trivy hoặc công cụ tương tự.
- Dùng Pod Security Admission/Kyverno để enforce policy.
- Cập nhật runtime và kernel thường xuyên.

Trong đề tài này, Container Runtime liên quan trực tiếp tới nhánh **Container Escape** và **Bad Pods** như privileged Pod, hostPath, hostPID hoặc mount runtime socket.

### CNI và Pod Networking

Ngoài kube-proxy, một cluster Kubernetes cần có thành phần networking để các Pod có thể giao tiếp với nhau. Phần này thường được triển khai bởi CNI plugin.

CNI là viết tắt của **Container Network Interface**. Đây là chuẩn giúp Kubernetes cấu hình network cho Pod.

Một số CNI phổ biến:

- Calico
- Cilium
- Flannel
- Weave Net

CNI chịu trách nhiệm cấp IP cho Pod, tạo route hoặc network rule cần thiết để Pod có thể giao tiếp với nhau trong cluster.

Trong Kubernetes, mỗi Pod thường có một IP riêng. Các Pod có thể giao tiếp trực tiếp với nhau qua IP này, kể cả khi chúng nằm trên các Node khác nhau, miễn là network plugin hỗ trợ.

Tuy nhiên, IP của Pod không ổn định. Khi Pod bị xóa và tạo lại, IP có thể thay đổi. Vì vậy, ứng dụng thường không nên giao tiếp với Pod bằng IP trực tiếp mà nên thông qua Service.

#### Góc nhìn bảo mật

Networking là phần cực kỳ quan trọng trong Kubernetes security vì nó quyết định attacker có thể di chuyển ngang trong cluster dễ hay khó.

Mặc định, nếu không cấu hình NetworkPolicy, nhiều cluster cho phép Pod ở các namespace khác nhau giao tiếp với nhau. Điều này làm tăng rủi ro lateral movement sau khi một Pod bị compromise.

Một số rủi ro:

- Không có NetworkPolicy, traffic giữa các Pod quá mở.
- Pod compromise có thể scan service nội bộ.
- Namespace bị hiểu nhầm là security boundary tuyệt đối.
- hostNetwork Pod có thể truy cập network giống như Node.
- Egress không kiểm soát, Pod có thể gọi ra Internet hoặc metadata service.

Một số hướng hardening:

- Áp dụng NetworkPolicy default deny cho ingress và egress.
- Chỉ mở traffic đúng nhu cầu giữa các app.
- Tách namespace theo trust boundary.
- Hạn chế hostNetwork.
- Theo dõi DNS/network connection bất thường.
- Nếu dùng Cilium, có thể tận dụng thêm Hubble hoặc Tetragon để quan sát runtime/network behavior.

##  Addons trong Kubernetes

Ngoài các thành phần cốt lõi, Kubernetes còn có các addon để bổ sung chức năng cho cluster. Addon không phải lúc nào cũng bắt buộc, nhưng trong thực tế hầu hết cluster production đều cần một số addon như DNS, monitoring, logging, ingress controller hoặc dashboard.


### DNS

DNS là addon rất quan trọng trong Kubernetes. Thành phần thường gặp nhất là CoreDNS.

DNS cho phép Pod và Service giao tiếp với nhau bằng tên thay vì phải nhớ IP.

Ví dụ, một Pod có thể gọi tới Service `mysql` trong namespace `default` bằng tên:

```text
mysql.default.svc.cluster.local
```

Thay vì phải gọi trực tiếp tới IP của Pod hoặc Service.

#### Góc nhìn bảo mật

DNS giúp service discovery dễ hơn, nhưng cũng có thể bị attacker lạm dụng để reconnaissance trong cluster.

Một số rủi ro:

- Pod compromise có thể query DNS để khám phá service nội bộ.
- DNS log có thể tiết lộ hành vi truy cập bất thường.
- Nếu CoreDNS bị cấu hình sai, có thể ảnh hưởng đến toàn bộ khả năng giao tiếp trong cluster.

Hardening gợi ý:

- Theo dõi DNS query bất thường.
- Hạn chế egress DNS nếu workload không cần.
- Bảo vệ CoreDNS deployment và RBAC của nó.
- Dùng NetworkPolicy để giới hạn Pod nào được gọi tới DNS nếu cần kiểm soát chặt.


### Dashboard

Kubernetes Dashboard là giao diện web giúp quan sát và quản lý cluster.

Thông qua Dashboard, người dùng có thể xem Pods, Deployments, Services, logs và trạng thái tổng quan của cluster. Tuy nhiên, trong môi trường production, Dashboard cần được bảo vệ rất cẩn thận.

#### Góc nhìn bảo mật

Dashboard từng là nguồn rủi ro lớn trong nhiều cluster vì nếu expose sai cách hoặc dùng token quyền cao, attacker có thể quản lý cluster qua giao diện web.

Một số rủi ro:

- Dashboard expose ra Internet.
- Bỏ qua authentication hoặc cấu hình authentication yếu.
- Dùng ServiceAccount có quyền quá cao.
- Token Dashboard bị lộ.

Hardening gợi ý:

- Không expose Dashboard public.
- Bảo vệ bằng authentication mạnh.
- Dùng RBAC least privilege.
- Không dùng token cluster-admin cho Dashboard.
- Theo dõi audit log cho các hành động đến từ Dashboard user/ServiceAccount.

### Monitoring và Logging

Monitoring giúp thu thập metrics như CPU, memory, số lượng Pod, trạng thái Node và trạng thái workload.

Logging giúp gom log từ container, Node và component hệ thống về một nơi tập trung để dễ tìm kiếm, phân tích và điều tra sự cố.

Một số công cụ phổ biến:

- Prometheus
- Grafana
- Loki
- Elasticsearch/OpenSearch
- Fluent Bit/Fluentd

Trong đề tài này, monitoring và logging còn liên quan đến detection. Ngoài log ứng dụng, ta cần quan tâm thêm:

- Kubernetes audit log
- Runtime alert từ Falco
- Event bất thường trong cluster
- Log từ API Server, kubelet, admission controller

#### Góc nhìn bảo mật

Nếu không có logging và monitoring, attack có thể xảy ra mà không để lại dấu hiệu dễ quan sát.

Một số hành vi nên theo dõi:

- Pod lạ được tạo trong namespace nhạy cảm.
- Tạo ClusterRoleBinding mới.
- ServiceAccount gọi API bất thường.
- Đọc Secret hàng loạt.
- Tạo privileged Pod hoặc Pod có hostPath.
- Exec shell trong container.
- Kết nối network bất thường giữa các namespace.

Hardening gợi ý:

- Bật Kubernetes audit log.
- Cài Falco để phát hiện runtime behavior nguy hiểm.
- Lưu log tập trung để phục vụ điều tra.
- Thiết lập alert cho hành vi liên quan đến privilege escalation.
- Định kỳ review RBAC và workload có cấu hình rủi ro.

## IV. Tổng kết phần kiến trúc dưới góc nhìn security

Qua các thành phần trên, có thể thấy Kubernetes không chỉ là một nền tảng chạy container mà là một hệ thống phân tán gồm nhiều lớp điều khiển, lưu trữ, thực thi và networking.

Từ góc nhìn bảo mật, mỗi thành phần đều có vai trò riêng trong attack surface:

- **API Server** là entry point để gọi Kubernetes API.
- **etcd** lưu toàn bộ trạng thái và dữ liệu nhạy cảm của cluster.
- **Scheduler** quyết định workload được đặt lên Node nào.
- **Controller Manager** tự động tạo/sửa/xóa tài nguyên để duy trì desired state.
- **kubelet** quản lý Pod trực tiếp trên Node và là attack surface quan trọng.
- **kube-proxy/CNI** quyết định cách traffic di chuyển trong cluster.
- **Container Runtime** là lớp thực thi container và liên quan trực tiếp tới container escape.
- **Addons** như Dashboard, DNS, Monitoring nếu cấu hình sai cũng có thể trở thành điểm yếu.

Đây là nền tảng quan trọng để bước sang phần tiếp theo: phân tích các kỹ thuật tấn công và leo thang đặc quyền trong Kubernetes. Đặc biệt, attack chain trọng tâm của leo thang đặc quyền sẽ xoay quanh việc attacker có shell trong Pod, lấy ServiceAccount token, gọi API Server, lạm dụng RBAC hoặc Pod misconfiguration, sau đó leo thang lên quyền cao hơn trong cluster.

## Tóm lại

Kubernetes Architecture được thiết kế theo mô hình phân tách rõ ràng giữa phần quản lý và phần thực thi.

**Control Plane** chịu trách nhiệm quản lý cluster, đưa ra quyết định và duy trì trạng thái mong muốn. **Worker Nodes** là nơi chạy các ứng dụng container hóa dưới dạng Pods.

Nhờ kiến trúc này, Kubernetes có thể tự động hóa nhiều công việc quan trọng như scheduling, scaling, self-healing, service discovery và rolling update. Đây cũng là lý do Kubernetes trở thành nền tảng phổ biến để triển khai và vận hành ứng dụng container trong môi trường hiện đại.









