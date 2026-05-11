# Literature Review

This table is a literature review as of May 2026, of recent studies that try to automate CFAST with tools such as RAVEN, CDATA or other custom scripts, whether to conduct Probabilistic Risk Assessment, perform sensitivity analysis, or generate data for machine learning.

| Date | Authors | Title | Description | Task | Sampled Scenarios | Coupling tool |
|------|---------|-------|-------------|------|-------------------|---------------|
| 2019 | Worrell et al. | Machine learning of fire hazard model simulations for use in probabilistic safety assessments at nuclear power plants [@WORRELL2019128] | Max upper layer temperature prediction in NPP fire scenarios | Regression | 675,000 | RAVEN |
| 2020 | Biersdorf et al. | Risk Importance Ranking of Fire Data Parameters to Enhance Fire PRA Model Realism [@osti_1632319] | Input parameter importance ranking for NPP Fire PRA | Sensitivity analysis | Morris EE + Monte Carlo (9 params) | RAVEN |
| 2020 | Buffington, Cabrera, Kurzawski, Ezekoye | Deep-Learning Emulators of Transient Compartment Fire Simulations for Inverse Problems and Room-Scale Calorimetry [@Buffington2020] | HRR inversion from thermocouples (CFAST pre-train, FDS fine-tune) | Regression | 20,000 | Custom Python script |
| 2021 | Fu, Tam et al. | Predicting Flashover Occurrence Using Surrogate Temperature Data [@Fu2021AAAI] | Flashover detection from temperature time series | Classification | 5,041 | CData |
| 2021 | Wang, Tam et al. | P-Flash – A machine learning-based model for flashover prediction using recovered temperature data [@WANG2021103341] | Temperature recovery + flashover prediction despite detector failure | Regression + Classification | 1,000 (main) + 4,000 (extended test set) | CData |
| 2021 | Fang, Lo, Zhang, Shen | Development of a machine-learning approach for identifying the stages of fire development in residential room fires [@FANG2021103469] | Fire development stage classification in residential rooms | Classification | 6,000 | None mentioned |
| 2021 | Kou, Wang, Guo, Zhu, Zhang | Deep learning based inverse model for building fire source location and intensity estimation [@KOU2021103310] | Fire room location and intensity identification | Classification | 970 | None mentioned |
| 2022 | Tam, Fu et al. | A spatial temporal graph neural network model for predicting flashover in arbitrary building floorplans [@TAM2022105258] | Cross-floorplan flashover prediction (scene-agnostic) | Classification | 78,000 | CData |
| 2022 | Kou et al. | A variational inference based learning approach for decentralized building fire estimation [@KOU2022105310] | Decentralized HRR estimation and fire location per building zone | Regression + Classification | 2,500 | CData |
| 2023 | Tam et al. | Generating Synthetic Sensor Data to Facilitate Machine Learning Paradigm for Prediction of Building Fire Hazard [@Tam2023_synthetic] | Fire location classification from synthetic detector data | Classification | 4,800 | CData |
| 2023 | Tam, Fu et al. | Real-time flashover prediction model for multi-compartment building structures using attention based recurrent neural networks [@TAM2023119899] | Real-time flashover prediction in multi-compartment home | Classification | 110,000 | CData |
| 2023 | Fan L., Tam W.C., Tong Q., Fu E.Y., Liang T. | An explainable machine learning based flashover prediction model using dimension-wise class activation map [@FAN2023103849] | Explainable flashover prediction with 30 s lead time | Classification | 60,000 | CData |
| 2024 | Yang, Zhang, Zhang, Tang, Ning, Zhang, Zhao | Fire Source Determination Method for Underground Commercial Streets Based on Perception Data and Machine Learning [@fire7020053] | Fire source location and intensity in underground commercial street | Classification | 4,800 | CData |
| 2024 | Singh, Bae, Zhang, Lim, Heo, Kim, Shin | Identification of primary input parameters affecting evacuation in ventilated main control room through CFAST simulations and application of a machine learning algorithm to replace CFAST model [@SINGH20243717] | MCR evacuation time prediction in NPP fire scenarios | Regression + Sensitivity analysis | 11,340 | None mentioned |
| 2024 | Jang, Singh, Lim, Bae, Heo, Zhang, Shin, Kim | Self- and semi-supervised learning for evacuation time modeling within fire emergencies in nuclear power plants [@JANG20241256] | MCR evacuation time with limited labels (NPP) | Regression | 11,880 | None mentioned |
| 2024 | Bui, Sakurahara, Reihani, Kee, Mohaghegh | Probabilistic Validation: Computational Platform and Application to Fire Probabilistic Risk Assessment of Nuclear Power Plants [@Sakurahara2024_probabilistic] | Probabilistic validation of CFAST cable damage in NPP switchgear room | Sensitivity analysis + Uncertainty quantification | ~25,000 (5,000 Morris + 20,000 MC) | RAVEN |
| 2025 | Alkhatib S., Sakurahara T., Reihani S., Mohaghegh Z. | A novel methodology to scientifically justify the formulation of modeling assumptions in screening analysis of Probabilistic Risk Assessment (PRA) [@ALKHATIB2025111237] | Justify ventilation modeling assumptions in NPP Fire PRA screening | Sensitivity analysis + Regression | 230,000 (206,786 after filtering) | None mentioned |
| 2026 | Zhang et al. | CFAST simulations and application of a machine learning algorithm for the fire safety of a switchgear room [@ZHANG2026104006] | Cable and cabinet damage time in NPP switchgear room | Regression | 6,480 | None mentioned |
| 2026 | Chen J., Sakurahara T. | Bayesian network-based surrogate model for physical simulation in probabilistic risk assessment of nuclear power plants [@CHEN2026111869] | Cable thermal damage probability for NPP Fire PRA screening | Regression | 20,000 | None mentioned |
| 2026 | Heo J., Zhang Y., Bae J., Lim S., Shin W.G., Kim S.B. | Explainable machine learning-based meta-modeling for predicting fire damage to motor control cabinets in a switchgear room [@HEO2026103862] | Cable and cabinet damage prediction with XAI in NPP switchgear | Regression | 6,480 | None mentioned |
| 2026 | Farajpour M., Nematollahi M., Pirouzmand A., Parsaei S. | Fire-induced risk assessment using probabilistic fire simulation and Dynamic event tree: A case study of a TRIGA research reactor [@FARAJPOUR2026114956] | Fire-induced core damage frequency for TRIGA research reactor | Uncertainty quantification | 10,000 | RAVEN |
| 2026 | Batikh et al. | A framework for multi-target temperature profile generation using functional PCA and Gaussian mixture models for Fire PRA [@BATIKH2026112333] | Multi-target correlated temperature profile generation for NPP Fire PRA | Generative modeling | 11,000 (after NUREG-1824 screening) | Custom (LHS sampling) |

Note on RAVEN–CFAST coupling : when RAVEN is listed as the coupling tool, it should be noted that coupling RAVEN to CFAST requires a Python interface implemented as a class inheriting from `CodeInterfaceBase`.

Example from [@WORRELL2019128] thesis below:

```python
from CodeInterfaceBaseClass import CodeInterfaceBase

class CFASTinterface(CodeInterfaceBase):
    def generateCommand(self,inputFiles,executable,clargs=None, fargs=None):
        todo = ''
        todo += clargs['pre']+' '
        todo += executable
        todo+=' RAVEN_CFAST'
        outfile = 'RAVEN_CFAST_zone'
        returnCommand = [('parallel',todo)],outfile
        print('Execution Command: '+str(returnCommand[0]))
    return returnCommand

    def createNewInput(self,currentInputFiles,origInputFiles,samplerType,**Kwargs):
        modDict = Kwargs['SampledVars']
        outfile=currentInputFiles[0]
        outfile.open('w')
        outfile.write('VERSN,6,RAVEN_CFAST\n')
        outfile.write('!!\n')
        outfile.write('!!Environmental Keywords\n')
        outfile.write('!!\n')
        outfile.write('TIMES,3600,50,10,10,0\n')
        ...
```