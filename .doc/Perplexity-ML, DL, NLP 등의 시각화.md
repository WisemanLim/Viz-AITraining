<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Machine learning, deep learning, neural network 등의 학습과정을 visualization해서 보여주는 오픈소스를 30개 정도 조사해서 비교 및 추천해 주세요

요청하신 것처럼 “학습 과정(Training Dynamics)”을 시각화해 주는 오픈소스들을 중심으로 약 30개를 조사해서, 유형별로 정리·비교하고 실전에서 쓸만한 것들을 추천드리겠습니다.[^1_1][^1_2][^1_3][^1_4]

***

## 1. 분류 기준 및 요약

먼저 범위를 조금 정리하겠습니다.[^1_3][^1_1]

- 대상: “ML/DL/NN 학습 과정을 시각화”하는 오픈소스
- 포함:
    - Loss/metric, 학습 곡선, 가중치, activation 변화 (시간축 중심)
    - 네트워크 구조 + 학습 상태 시각화
    - Feature/attribution, latent space 등 학습 결과의 동적 관찰 도구
- 제외(또는 부차적): 단순 BI/대시보드, 일반 plot 라이브러리(단, ML 특화 기능 있으면 포함)

유형은 대략 네 가지로 나눴습니다.[^1_2][^1_1][^1_3]

1. 프레임워크 통합형 (TensorBoard, PyTorch 계열, Keras 등)
2. 모델/아키텍처 시각화 특화 (Netron, TensorSpace, Visualkeras 등)
3. 학습 동작·설명 가능성(XAI) 분석 (ActiVis, LSTMVis, SHAP, LIME 등)
4. 교육·실험용 인터랙티브 툴 (TensorFlow Playground, GAN Lab, RNNbow 등)

아래에서 약 30개를 리스트업하고, 마지막에 “실전 추천 세트”를 정리하겠습니다.

***

## 2. 대표 도구 30개 리스트

### 2.1 프레임워크 통합형 / 실습용 대시보드

1. **TensorBoard** (TensorFlow 공식)[^1_5][^1_2][^1_3]
    - 기능: 그래프(연산 그래프), scalar(손실·정확도), 가중치 histogram, 이미지/embedding projector, profile.[^1_5][^1_2]
    - 특징: TensorFlow/Keras는 거의 표준, PyTorch에서도 SummaryWriter로 일부 사용 가능.[^1_2]
2. **Keras 내장 시각화 (plot_model 등)**[^1_4][^1_6]
    - 기능: Graphviz 기반 네트워크 구조 다이어그램, callback으로 history(Loss/metric) plot 가능.[^1_6][^1_4]
    - 특징: 구조 이해용, 실시간보다는 정적에 가깝지만 fit 과정은 간단하게 그릴 수 있음.[^1_6]
3. **Netron**[^1_2][^1_6]
    - 기능: 다양한 포맷(ONNX, TensorFlow, PyTorch 등) 모델 구조를 시각적으로 탐색.[^1_6][^1_2]
    - 특징: 레이어별 파라미터·shape·연결 관계를 웹 UI에서 인터랙티브하게 확인.[^1_2]
4. **NVIDIA DIGITS (과거)**[^1_7]
    - 기능: Caffe/TensorFlow 기반 이미지 분류/검출 학습을 웹 UI에서 관리하고, loss/accuracy 및 샘플 예측을 시각화.[^1_7]
    - 특징: 현재는 사실상 유지보수 중단 수준이지만, “학습 과정 웹 UI”의 좋은 레퍼런스.[^1_7]
5. **Orange**[^1_7]
    - 기능: 드래그 앤 드롭 워크플로우로 데이터 전처리, 모델 학습, 평가, 시각화까지 지원.[^1_7]
    - 특징: 오픈소스 ML+시각화 툴킷, widget으로 모델 평가 및 학습 곡선 확인.[^1_7]
6. **KNIME**[^1_7]
    - 기능: 노드 기반 워크플로우, 모델 학습 및 다양한 시각화 노드 제공.[^1_7]
    - 특징: 순수 DL 전용은 아니지만, ML 파이프라인 전체를 시각적으로 표현 가능.[^1_7]
7. **Apache Superset** (BI지만 ML 모니터링에 사용 가능)[^1_8]
    - 기능: 대시보드·차트 작성, SQL 기반.[^1_8]
    - 특징: MLflow 등에서 로그를 DB에 쌓고 Superset으로 시각화하는 패턴에 적합.[^1_8]
8. **MLflow**[^1_8]
    - 기능: 실험 추적, 파라미터/metric 그래프, 모델 레지스트리.[^1_8]
    - 특징: 모델 구조 자체를 시각화하진 않지만, 학습 과정 메트릭 시각화에 사실상 표준.[^1_8]
9. **Yellowbrick**[^1_2]
    - 기능: scikit-learn용 시각화 라이브러리 (학습 곡선, ROC, 잔차 등).[^1_2]
    - 특징: 고전 ML 중심이지만 딥러닝 이전 단계(전처리/모델선정) 분석에 유용.[^1_2]
10. **TensorBoard.dev / Poloclub 계열의 예제**
    - TensorBoard 자체의 hosted 버전은 OSS는 아니지만, Poloclub 그룹이 다양한 DL 시각화 도구를 제공.[^1_9]

### 2.2 네트워크 구조/아키텍처 시각화 특화

GitHub `Tools-to-Design-or-Visualize-Architecture-of-Neural-Network` 리포지토리가 이 영역 도구를 잘 정리하고 있습니다.[^1_4]

11. **TensorSpace**[^1_4]
    - 기능: TensorFlow.js + Three.js 기반 3D 신경망 시각화 프레임워크.[^1_4]
    - 특징: Browser에서 3D로 레이어, activation을 인터랙티브하게 관찰 가능.[^1_4]
12. **Visualkeras**[^1_4]
    - 기능: Keras 모델 구조를 미려한 2D 레이어 다이어그램으로 그려줌.[^1_4]
    - 특징: 논문/발표용으로 인기, 구조 이해에 좋지만 학습 시간축 시각화는 제한적.[^1_4]
13. **Net2Vis**[^1_4]
    - 기능: Keras 코드에서 CNN 구조를 자동으로 추상 다이어그램으로 변환.[^1_4]
    - 특징: 논문 피겨 생성 자동화에 최적.[^1_4]
14. **PlotNeuralNet**[^1_4]
    - 기능: LaTeX(TikZ) 기반 CNN 도식 생성 스크립트.[^1_4]
    - 특징: 완전히 정적이지만, 구조 표현용으로 정석 레벨; time dynamics는 별도.[^1_4]
15. **NNSVG**[^1_4]
    - 기능: 웹 기반 NN 구조 SVG 생성기.[^1_4]
    - 특징: 직관적인 구조 그림, 교육용에 적합.[^1_4]
16. **draw_convnet**[^1_4]
    - 기능: ConvNet 구조를 그리는 Python 스크립트.[^1_4]
17. **keras-sequential-ascii**[^1_4]
    - 기능: 터미널에서 ASCII 아트로 Keras Sequential 모델 구조 출력.[^1_4]
18. **Conx**[^1_4]
    - 기능: Python 패키지로, 네트워크 구조와 activation을 함께 시각화(net.picture).[^1_4]
    - 특징: 교육/데모에서 “각 레이어 활성화”를 보여주기 좋음.[^1_4]
19. **Netscope CNN Analyzer**[^1_4]
    - 기능: Caffe prototxt를 CNN 다이어그램으로 표현.[^1_4]
20. **Moniel (Monial)**[^1_4]
    - 기능: 계산 그래프를 인터랙티브하게 시각화하는 표기법/툴.[^1_4]
21. **nn_vis (Neural Network Visualization)**[^1_10]
    - 기능: Python + OpenGL/Pygame으로 네트워크를 인터랙티브 시각화, 데이터 흐름을 안내.[^1_10]
    - 특징: 교육용으로 학습 시 데이터가 어떻게 레이어를 통과하는지 보여주는 예제.[^1_10]

### 2.3 학습 동작·설명가능성(XAI) 시각화 도구

이 영역은 “Visual Analytics in Deep Learning” 설문 논문과 XAI survey에 많이 정리돼 있습니다.[^1_11][^1_12][^1_1][^1_3]

22. **ActiVis**[^1_3]
    - 목적: 대규모 DNN의 내부 activation과 예측 결과를 탐색하는 시각 분석 시스템.[^1_3]
    - 특징: hidden layer 활성화와 데이터 인스턴스를 연동해서 디버깅하는 용도.[^1_3]
23. **LSTMVis**[^1_3]
    - 목적: RNN/LSTM hidden state 동작을 시각적으로 분석.[^1_3]
    - 특징: 시퀀스 상에서 어떤 패턴에 어떤 상태가 반응하는지 시각적 탐색 지원.[^1_3]
24. **RNNbow**[^1_3]
    - 목적: RNN에서 backpropagation gradient 흐름을 시각화.[^1_3]
    - 특징: 학습 중 gradient vanishing/exploding을 시각적으로 파악.[^1_3]
25. **DeepEyes**[^1_3]
    - 목적: DNN 설계·튜닝을 위한 progressive visual analytics 시스템.[^1_3]
26. **Seq2Seq-Vis**[^1_3]
    - 목적: Seq2Seq 모형(번역 등)의 attention과 hidden state를 시각화하여 디버깅.[^1_3]
27. **GAN Lab**[^1_3]
    - 목적: 인터랙티브하게 GAN 훈련 과정을 시각화.[^1_3]
    - 특징: decision boundary, generator/real data 분포, gradient 흐름 등을 시각적으로 보여줌.[^1_3]
28. **GANViz**[^1_3]
    - 목적: GAN adversarial game의 훈련 과정을 분석하는 시각 분석 도구.[^1_3]
29. **Analyzing the Training Processes of Deep Generative Models** 관련 도구[^1_3]
    - 논문과 함께 제공되는 시각 분석 시스템으로, VAE/GAN 등 generative model 학습 과정 시각화.[^1_3]
30. **LIME**[^1_2]
    - 기능: 복잡한 모델을 국소적으로 선형 모델로 근사해 각 feature의 기여를 시각화.[^1_2]
    - 특징: 학습 중 보다는 학습 후 예측 설명용이지만, 반복적으로 호출하면 학습 진행 중 feature 중요도 변화를 살펴볼 수 있음.[^1_2]
31. **SHAP**[^1_2]
    - 기능: Shapley 값 기반 feature importance를 global/local로 시각화.[^1_2]
    - 특징: 트리/NN 포함 거의 모든 모델에 적용 가능, 시간축을 따라 shap value 변화를 트래킹하면 “학습된 패턴”을 분석 가능.[^1_2]

### 2.4 교육·데모용 인터랙티브 시각화

딥러닝 시각화 survey와 관련 사이트에 예제가 정리돼 있습니다.[^1_1][^1_9][^1_3]

32. **TensorFlow Playground**[^1_13][^1_1]
    - 기능: 브라우저에서 간단한 fully-connected NN를 실시간 학습, decision boundary와 loss 변화를 애니메이션으로 시각화.[^1_13][^1_1]
33. **Teachable Machine (Google)**[^1_1]
    - 기능: 웹캠/이미지/오디오로 수 분 내에 모델을 학습하고 결과를 시각화.[^1_1]
    - 특징: 코드보다는 UX 중심, 교육·시연에 최적.[^1_1]
34. **Deep Visualization Toolbox**[^1_1]
    - 기능: CNN 내부 filter/activation을 실시간으로 시각화하는 데스크탑 도구.[^1_1]
35. **How to Use t‑SNE Effectively 예제 구현들**[^1_1]
    - 기능: t‑SNE 기반으로 embedding/latent space를 시각화하여 높은 차원의 feature 변화를 확인.[^1_1]
36. **Dataset 시각화 도구 – Activeloop app.activeloop.ai**[^1_14]
    - 기능: 이미지/레이블/bbox/segmentation을 빠르게 시각화하여 데이터셋 품질을 탐색.[^1_14]
    - 특징: 학습 전 단계지만, “데이터 문제 vs 모델 문제”를 구분하는 데 중요.[^1_14]

***

## 3. 요약 비교 표

아래 표는 “딥러닝 학습 과정 모니터링/분석” 관점에서 핵심적인 도구 몇 개만 추려 비교한 것입니다.[^1_5][^1_8][^1_2][^1_3][^1_4]


| 도구 | 주요 목적 | 학습 시간축 시각화 | 내부 상태(activation 등) | 아키텍처 시각화 | 주요 스택/대상 |
| :-- | :-- | :-- | :-- | :-- | :-- |
| TensorBoard | TF 모델 학습 모니터링 | 손실·metric·profile[^1_5][^1_2] | 가중치 histogram, embedding[^1_2] | 그래프 구조[^1_5] | TensorFlow/Keras 중심[^1_5] |
| MLflow | 실험 관리·모델 추적 | metric 곡선[^1_8] | 없음(로그 기반) | 없음 | 프레임워크 불문[^1_8] |
| Netron | 모델 구조 탐색 | 없음 | 일부 tensor 정보[^1_2] | 상세 구조[^1_2][^1_6] | ONNX/TF/PT 등[^1_2] |
| TensorSpace | 3D NN 구조·activation 시각화 | step 단위 갱신[^1_4] | activation 레벨[^1_4] | 3D 구조[^1_4] | TF.js/Keras 등 사전 학습 모델[^1_4] |
| Visualkeras | 구조 그림 생성 | 없음 | 없음 | 미려한 구조도[^1_4] | Keras 모델[^1_4] |
| ActiVis | 대규모 DNN 시각 분석 | epoch/step 뷰[^1_3] | activation/클러스터[^1_3] | 추상 구조 | 대규모 산업용 NN[^1_3] |
| LSTMVis | RNN/LSTM 상태 분석 | 시퀀스 상 동작[^1_3] | hidden state 동역학[^1_3] | 간략 구조 | RNN 계열[^1_3] |
| RNNbow | RNN gradient 분석 | BPTT gradient 흐름[^1_3] | gradient 규모[^1_3] | 간략 구조 | 교육·디버깅[^1_3] |
| GAN Lab | GAN 교육용 시뮬레이터 | training 애니메이션[^1_3] | decision boundary 등[^1_3] | 단순 구조 | 브라우저 기반 실험[^1_3] |
| SHAP | 예측 설명(XAI) | 수동 반복 시 가능[^1_2] | feature 기여도[^1_2] | 없음 | 모델 불문[^1_2] |
| LIME | 예측 설명(XAI) | 수동 반복 시 가능[^1_2] | 국소적 feature 영향[^1_2] | 없음 | 모델 불문[^1_2] |
| nn_vis | NN 데이터 흐름 교육 | 인터랙티브 step[^1_10] | 레이어별 활성화[^1_10] | 간단 구조 | Python/OpenGL[^1_10] |
| Conx | 구조+activation 시각화 | step 기반[^1_4] | activation 그림[^1_4] | 간단 구조 | Python[^1_4] |
| Yellowbrick | 고전 ML 모델 진단 | 학습 곡선 등[^1_2] | 없음 | 없음 | scikit-learn[^1_2] |


***

## 4. 실전 관점 추천 시나리오

Wiseman 님 상황(엔터프라이즈·연구 환경, Kubernetes/LLM/RAG 경험) 기준으로, “실 사용 가치” 위주로 조합을 제안하면 다음과 같습니다.

### 4.1 연구·프로토타입 (PyTorch/TF 혼용)

- **기본 세트**
    - TensorBoard (혹은 PyTorch의 SummaryWriter 연동)[^1_5][^1_2]
    - MLflow (실험·하이퍼파라미터 관리)[^1_8]
- 역할 분담
    - TensorBoard: 단일 run 안에서 loss, accuracy, gradient histogram, activation/embedding projector까지 실시간 모니터링.[^1_5][^1_2]
    - MLflow: 실험 간 비교(파라미터 조합 vs 결과), 다중 모델/데이터셋 관리.[^1_8]

이 조합으로 “학습 로그 + 메타데이터”는 상당 부분 커버됩니다.

### 4.2 모델 구조/발표용 아키텍처 시각화

- **추천 조합**
    - Netron (실제 export된 모델 구조 디버깅)[^1_6][^1_2]
    - Visualkeras 또는 PlotNeuralNet / Net2Vis (논문·발표용 구조 그림)[^1_4]
- 활용 패턴
    - 개발 중에는 Netron으로 실 모델(ONNX 등)의 레이어·shape 확인 및 버그 탐지.[^1_6][^1_2]
    - 설계/발표 단계에서는 Visualkeras/PlotNeuralNet으로 abstraction된 그림 생성.[^1_4]


### 4.3 RNN/시퀀스·GAN 등 복잡 모델 디버깅

- **RNN, 시퀀스 모델**
    - LSTMVis, RNNbow[^1_3]
    - 필요 시 Seq2Seq-Vis 활용[^1_3]
- **GAN, 생성 모델**
    - GAN Lab, GANViz, “Analyzing the Training Processes of Deep Generative Models” 도구군[^1_3]

이들은 대체로 논문 구현 레벨이라, 실제 코드에 붙여 쓸 때는 해당 리포지토리를 포크해서 로그 포맷을 맞추는 작업이 필요합니다. 연구용으로는 상당히 강력합니다.[^1_3]

### 4.4 XAI / Feature 관점 시각화

- **실무(엔터프라이즈) 추천**
    - SHAP + LIME + 일반 plotting(matplotlib/Plotly)[^1_15][^1_2]
- PoC 예
    - 주기적으로 체크포인트 저장 → 해당 시점의 모델에 대해 SHAP/LIME 계산 → feature importance/partial dependence를 시간축으로 붙여서 “학습 진행에 따른 decision boundary 변형”을 보는 대시보드 구축.[^1_2]
    - 이 때 시계열 시각화는 Superset/Plotly Dash로 묶으면 좋습니다.[^1_16][^1_8]

***

## 5. “30개 중에서 무엇을 시작할까?” 제안

관심사(연구+엔터프라이즈+K8s) 기준으로 **우선순위**를 정리하면:

1. **반드시 도입할 것**
    - TensorBoard (또는 PyTorch equivalent)[^1_5][^1_2]
    - MLflow (실험 관리 플랫폼)[^1_8]
2. **구조/디버깅·발표용**
    - Netron (모델 파일 디버깅)[^1_6][^1_2]
    - Visualkeras 또는 PlotNeuralNet/Net2Vis (아키텍처 다이어그램)[^1_4]
3. **고급/연구용 시각 분석**
    - ActiVis, LSTMVis, RNNbow, GAN Lab/ GANViz, DeepEyes 등 논문 도구군 (필요 모델 유형에 따라 선택)[^1_3]
4. **설명가능성·엔터프라이즈 보고**
    - SHAP, LIME + Superset/Plotly 기반 커스텀 대시보드[^1_16][^1_8][^1_2]

이 정도면 “실험·제품·연구 발표” 세 영역 모두에서 재사용이 가능할 것입니다.

***

혹시 “실시간으로 학습 중인 PyTorch 모델의 weight/activation을 웹에서 인터랙티브하게 보는 커스텀 대시보드”처럼 더 구체적인 목표가 있으신가요? 그 경우에는 위 도구들 중 어떤 것을 코어로 삼고, 어떤 부분을 직접 개발해야 할지까지 아키텍처 레벨로 같이 설계해 보겠습니다.
<span style="display:none">[^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30]</span>

<div align="center">⁂</div>

[^1_1]: https://subinium.github.io/LR014/

[^1_2]: https://machinelearningmastery.com/5-tools-visualizing-machine-learning-models/

[^1_3]: https://www.sciencedirect.com/science/article/pii/S2468502X1830038X

[^1_4]: https://github.com/ashishpatel26/Tools-to-Design-or-Visualize-Architecture-of-Neural-Network

[^1_5]: https://goatlab.tistory.com/entry/딥러닝-프레임워크-비교

[^1_6]: https://www.coursera.org/articles/neural-network-visualization

[^1_7]: https://primo.ai/index.php?title=Graphical_Tools_for_Modeling_AI_Components

[^1_8]: https://velog.io/@shinichi77/2025-top-10-dev-tools

[^1_9]: https://poloclub.github.io

[^1_10]: https://sourceforge.net/projects/neural-network-vis.mirror/

[^1_11]: https://pmc.ncbi.nlm.nih.gov/articles/PMC6703958/

[^1_12]: https://www.sciencedirect.com/science/article/abs/pii/S0097849321001886

[^1_13]: https://www.reddit.com/r/MachineLearning/comments/un4jv9/d_is_there_a_tool_to_visualise_my_neural_network/

[^1_14]: https://www.reddit.com/r/MachineLearning/comments/klw7pt/p_appactiveloopai_a_free_tool_to_quickly/

[^1_15]: https://www.oracle.com/kr/artificial-intelligence/machine-learning/

[^1_16]: https://docs.kanaries.net/ko/articles/open-source-data-visualization-tools

[^1_17]: https://developers-kr.googleblog.com/2017/08/facets-open-source-visualization-tool.html

[^1_18]: https://www.reddit.com/r/BusinessIntelligence/comments/vh9kwt/open_source_bi_tools_what_are_your_thoughts_on/

[^1_19]: https://blog.naver.com/ydk531/222101900426

[^1_20]: https://blog.naver.com/mouserkorea/222540386756

[^1_21]: https://newsight.tistory.com/180

[^1_22]: https://kr.mathworks.com/products/deep-learning.html

[^1_23]: https://kr.mathworks.com/help/deeplearning/visualize-and-verify-deep-neural-networks.html

[^1_24]: https://accesson.kr/jkda/assets/pdf/44553/journal-60-5-299.pdf

[^1_25]: https://github.com/fredhohman/visual-analytics-in-deep-learning

[^1_26]: https://github.com/axruff/DeepLearning

[^1_27]: https://github.com/NiuTrans/ABigSurvey

[^1_28]: https://www.hse.ru/data/2023/04/27/2028792236/4.pdf

[^1_29]: https://ieeexplore.ieee.org/document/8882046/

[^1_30]: https://www.computer.org/csdl/journal/tg/2024/12/10412199/1TWoWI1yZ8s

