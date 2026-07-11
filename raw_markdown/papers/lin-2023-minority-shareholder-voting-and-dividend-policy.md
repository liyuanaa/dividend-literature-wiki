> Full text available from PDF conversion (markitdown).

# Minority Shareholder Voting and Dividend Policy

- **Authors:** Lin, Jing; Li, Fang; Zheng, Steven Xiaofan; Zhou, Mingshan
- **Journal:** Journal of Banking and Finance
- **Year:** 2023
- **DOI:** 10.1016/j.jbankfin.2022.106748

## Abstract

We find that minority shareholders' voting opposition to dividend proposals is associated with significantly higher cash dividend payout in the following year for stocks listed in Shanghai Stock Exchange. When minority shareholders' voting opposition increases, the likelihood and frequency of regulatory penalties increase. The reverse happens after firms increase dividend payout. Minority shareholders' voting opposition has a stronger positive effect on cash dividend payout when they post more messages in stock forums and when independent directors express dissenting opinions. The effect is weaker if the board chair or CEO has political connections. Minority shareholders' voting opposition does not have significant effects on the growth rate of earnings and the level of earnings management. But we do find evidence that minority shareholder voting opposition reduces expropriation by major shareholders. The evidence supports a hypothesis that regulators use the minority shareholder voting results to screen out possible cases of shareholder oppression.

## Journal of Banking and Finance 148 (2023) 106748

**JEL Classification:** G34, G35

**Keywords:** Minority shareholder; Voting; Dividend; Regulation; Expropriation

### 1. Introduction

In China, the China Securities Regulatory Commission (CSRC) requires that listed firms should fully listen to the voting opinions and demands of minority shareholders when reviewing dividend proposals. The Shanghai Stock Exchange (SSE) recommends firms with positive earnings to maintain a minimum cash dividend payout ratio of 30% starting from 2013. Profitable firms failing to reach this minimum are required to disclose minority shareholder voting details regarding the dividend decision.

**Vote disclosure screening hypothesis:** Because disclosure of minority voting opposition to dividend proposals triggers additional regulatory scrutiny, firms are more likely to increase dividend payout to avoid the attention of regulators. Regulators use minority shareholder voting results to screen out possible cases of shareholder oppression.

### 2. Institutional Background

**SSE Dividend Guidelines (January 2013):** Firms with positive earnings but payout < 30% must disclose: (a) specific reasons for non-compliance; (b) provide online voting opportunities for investors; (c) disclose voting results broken down by holding-percentage intervals.

**Regulatory enforcement mechanisms:**
- SSE required 182 companies (2014) to call information meetings, submit plans to a shareholder vote, and disclose results.
- Non-compliance leads to: regulatory letters of concern → notices of criticism → public censures → CSRC inspection → administrative penalties.
- Penalties affect directors' qualifications, firms' equity re-financing ability (no public offerings/private placements for 36 months after CSRC penalties), and executives' career prospects.

Key examples: SSE issued regulatory letters to multiple firms (Dongan, Jinbei, Fangda, Sichuan Languang) for failing to meet dividend requirements.

### 3. Sample and Descriptive Statistics

**Sample:** SSE A-share firms, 2013–2019. Excludes: financial firms, B-share and H-share firms, observations with negative retained earnings, and voluntary disclosers (to avoid endogeneity). Sample = 1,989 firm-years from firms that did NOT meet the 30% minimum payout recommendation.

**Minority voting data:** Manually collected from general meeting resolutions. Dissent = percentage of votes against + percentage of abstentions among minority shareholders.

**Summary statistics (Table 3):**
- Mean Attendance = 49.59%
- Mean Dissent = 9.293% (median = 0.201%)
- Mean SMCover (log messages in stock forums) = 7.527 (≈ 1,858 messages)
- IndDissent = 0.014 (1.4% of firm-years have independent director expressing dissent)
- PolConnection = 0.089 (8.9% have politically connected board chair or CEO)

Table 1: Firms not meeting 30% minimum increased from 105 (11.1% of SSE firms) in 2013 to 484 (33.5%) in 2019. Dissent decreased over time (mean 18.984% in 2013 → 8.128% in 2019).

### 4. Empirical Results

**4.1.1 Factors affecting minority shareholder opposition (Table 4):**
Regression (1): Dissent = α + β Dividend_{i,t} + Σ Controls + firm FE + year FE + ε

- Lower dividend payout causes significantly higher minority voting opposition.
- For each one SD decrease in Dividend2E, opposing votes increase by >10.6% relative to the mean.
- If no dividend proposed: opposing votes increase by 7.538% (≈81.1% relative to mean).

**4.1.2 Effect on future dividends (Table 5):**
Regression (2): Dividend_{i,t} = α + β Dissent_{i,t-1} + Σ Controls + firm FE + year FE + ε

- One SD increase in Dissent → Dividend2E_After increases by 8.6% relative to mean.
- One SD increase in Dissent → DividendDum_After increases by 2.2 pp; Dividend2A_After increases by 7.4%.
- PSM tests using SZSE control sample confirm: treatment × Dissent coefficient positive and significant (14% relative increase in Dividend2E_After per SD of Dissent).

**4.2.1 Director reputation channel (Table 7):**
Interaction Dissent × Reputation (Directors_Age and Directorships): all insignificant. Not supported.

**4.2.2 Major shareholder reputation channel (Table 8):**
Dissent does not significantly affect PIPE success or market reaction (CAR) to major shareholder holding announcements. Not supported.

**4.2.3 Regulatory screening channel (Table 9):**
- H2a: One SD increase in Dissent → 33% increase in number of regulatory penalties (significant at 5%).
- H2b: DividendHikeDum (firms that increased dividends) → 43.3% decrease in regulatory penalties.

**4.3 Source of dividend increase:**
Minority voting opposition is negatively associated with Tunneling (other receivables / total assets), i.e., reduces intercorporate loans to related parties. Perk consumption (Abperks_Indirect and Abperks_Direct) not significantly affected. Main channel: reduction of expropriation by major shareholders, not earnings management.

**4.4 Moderators:**
- SMCover (stock forum messages): positive moderator — effect of Dissent on dividends is stronger when minority shareholders post more messages.
- IndDissent (independent director dissenting opinions): positive moderator.
- PolConnection (political connections of board chair or CEO): negative moderator — effect significantly weaker.

### 5. Conclusion

The evidence supports the vote disclosure screening hypothesis: in China's regulatory environment, minority shareholder voting opposition to dividend proposals serves as a screening signal for regulators, triggering regulatory scrutiny. Firms preemptively increase dividends to avoid this scrutiny. The mechanism operates through reduced expropriation of minority shareholders by major shareholders, not through changes in earnings or management perks. The paper has important policy implications: regulators in markets with concentrated ownership should encourage minority shareholder voting and require disclosure of voting details on dividend decisions.
