function y1 = alk_nng2_vel13(x1)
% [y1] = talk_nnet(x1) takes these arguments:
%   x = 9xQ matrix, input #1
% and returns:
%   y = 1xQ matrix, output #1
% where Q is the number of samples.

%#ok<*RPMT0>

%x1=x1';
%%
%LONGITUDE, LATITUDE, DEPTH, THETA, SAL, NITRAT, PHSPHT, SILCAT, OXY
LONGITUDE=1;
SAL=5;
x1(LONGITUDE,:)=mod(x1(LONGITUDE,:) + 180, 360) - 180;

% ===== NEURAL NETWORK CONSTANTS =====

% Input 1
x1_step1.xoffset = [-179.988;-78.638;0;-2.18999374712659;32;0;0;0;0];
x1_step1.gain = [0.00555574074691379;0.0118597231940607;0.000266427808795185;0.0582080345370401;0.232207128758853;0.0396691353384097;0.112324926377178;0.00805941301515655;0.0019476093095725];
x1_step1.ymin = -1;

% Layer 1
b1 = [-0.92409777024623218633;26.38817429377832724;57.950805996110737794;-56.291305529739737779;-82.132041633109579948;1.6645572528330363493;-5.2269197136311404961;-46.3809029608363943;36.703986856197793998;-5.0586227115039719138;5.0659031161226257822;-5.8084594929569766109;-101.80195755007419223;-11.480396410799986739;39.7412025338207755;-84.248055998779278752;45.489817845532023455;-173.38958319303867484;20.634217428673732542;-1.1701786336691295531;-111.01960201482185653;-7.6682904656909132157;-139.02188947007408615;-64.664840186397071875;-32.189870204459964498;2.8889804435221035916;-2.0435632413340933944;-77.296621333775888729;12.185866365698981184;-19.074051454297769936;-34.827628383474653617;-3.7205445207340503977;-4.4516363029425685127;-3.8578647810421178299;-30.176619537462105569;15.966197621395737727;-4.7294505681430800692;-61.675548977441955856;78.826492958597839333;107.38052104508098239;-25.764970874028211512;128.16606214837264588;-21.114106541519852556;-10.238766455560588398;-4.8115158199303857955;-20.905349430181573211;40.610915060270166066;4.5420828453359529675;18.65997273306744475;4.5690333138333301122;-45.331963370437385663;9.5873759436681353918;60.681208064689144521;-39.338531830053241833;2.7344676051406726636;26.872496764941416814;34.106195264069846473;92.710942322712412533;51.353186850530200047;-11.168674448774771335;-36.458228622094658533;-9.3462389215204701998;7.7601749120290195449;101.34221145658329988];
IW1_1 = [20.931836698419889586 72.747359066133228112 -89.684002394681755277 -13.016120982885313495 -49.853454363400921068 -59.505015300720835114 8.5718823699590380727 101.37769222326437557 47.553210855387206379;5.8296968322669489027 1.4600937992218341321 -1.288523091154225142 1.1830167005263727553 15.968264181783819566 -0.75757314808635844994 22.3954791785572489 3.6937689732280420962 10.587282878995806001;13.764696862323578586 -2.1138797674689548955 4.6364935346493583168 14.124927407237404253 26.608510949775535437 -2.3964116758292237641 40.836666509029484473 -3.1644436042264643127 4.0435200210759489892;5.1063060536691580182 -1.3471997328889266932 2.5256299132383768224 -3.8100312072829378707 6.6237508177425103995 6.4164258092724599791 -62.815363984667968111 1.6754902326389295997 -7.8969975596575867627;-1.3606103148529793412 -20.566262312592229478 -15.29784505497434921 33.763996694029216883 -12.433797492452312028 44.199080991550161457 -158.58881677673306854 21.592537554520635723 46.204380742360278589;-3.2915405626589371302 -1.7324644036061551677 0.47561529031071403395 -1.6051985715715777481 -0.57668377840614049035 -2.2990237210439548043 1.7149445306395483257 4.0515039281422202677 -1.0568555991748893597;-1.7570980930809909637 0.61267154361709652566 -0.18582298050982695714 -1.7831085120312455405 -0.67263133728440294146 -0.91319133801254348537 -3.3588172741586799219 0.47813969493332592053 -1.6730921241736993466;-15.006426965363704795 3.0698305451903245 -110.69998874942682221 -36.500815918934698345 68.971406270578555109 47.51388654578123294 0.58434747927572427972 12.196008572734431397 0.037942369568419606618;-7.0735580016212660226 10.699747841265740078 -14.513402721465714862 27.694991403164394228 69.313894402096039471 57.518790680227006362 -95.267041482982989464 10.561743983588456786 108.27932020012930536;0.016347251566432689091 0.81043563131820461898 -0.009032564129030563882 0.10746555222907776261 -1.1275716248288845112 1.8771822182132427148 -3.7875530848616594248 -0.32829422441073302652 -4.3161533546022301522;1.7617713141387645326 -0.59546980586343911668 0.18929427090193148842 1.8015482769053803302 0.62630222607603314167 0.95498069678058905563 3.122124362095447303 -0.45184202984170268591 1.6871962126632822354;0.15843372805944966331 2.9940652741824789196 -1.3309721698840695225 -6.0133017338635443849 -14.779594405059096829 -12.759029441569424534 22.688049753647973716 -1.3150893099512941387 -17.947770276516436638;-34.403544347308560702 -12.813442361536479197 39.151295008334720649 -4.3824371906834551638 -2.3493571970133291238 -28.392061412468859061 -121.36925414098826081 -1.8543652192549391344 -53.926933762703313846;-0.74399418001502426456 -3.9425391866267736063 1.3540093131698429652 -5.5248664126105317962 16.375069142594405491 -0.13256393455840778661 -17.124915402435757272 -6.9793753696334128733 1.8055506338523947818;0.71699205329212467586 -0.39686106528584635944 18.50240109169370939 3.0971670217390396829 -0.59320867408883692917 16.95114836437166872 7.2598564442596913437 -19.208584344697488433 36.857973685371803185;5.7198412889392802327 -0.61930515060159474494 -21.271191671996788841 -0.91892418139578335712 -1.6870830588515919324 11.302034311711100401 -97.53916448049787391 15.677013162358521825 -5.2134572489202382073;6.6604169783941973293 -8.5479854966996384746 12.473584895620314583 -21.500632298853826541 4.2494802360200889524 -17.673753541540786927 74.26867237969297264 -10.28275949581092874 -29.994069498497324844;-16.562676149124342828 -22.810682323727199616 -8.0168965394233779875 -59.690509763277326272 -34.197640447556615584 -37.678564844712852278 -90.183170613896592727 15.331181792774390971 -109.11600498117978475;-14.721131708802579041 2.8757247863981234559 -19.64776872006549624 12.423836116624682901 -28.243723766397234698 13.89798349100102115 8.4119249255482859695 47.101377243700191855 -20.2625781061340966;-0.21978085334347094437 2.7804958050549362092 -2.8867883678058339214 7.986870225709648885 -16.240403531332695763 1.8708689446353639063 -11.668079750412506002 0.48667403089699240448 10.254625400553583958;0.2400506133670565756 -36.140291937920331122 -89.932770363366500987 12.64390184845338716 -3.3433354144580591516 -26.298379866712444652 -70.438929760102837463 99.693546153059628523 -31.520406704109287688;-5.3495187188363555464 -2.6145322245418167739 -0.18204278479175736716 -3.1626688204966626472 1.5760117061135674454 -1.5026320122913552346 -9.3938740754270479982 0.63157320484629086987 -2.4785556413373277529;24.176659503006796115 -4.4983265051003744617 12.127896020419150602 -63.597200896887216004 -28.229193692478883548 -35.234347049223103454 -113.69735349263858382 3.5806893498417609045 8.912362775451740049;1.5016880061576971528 -1.9340596474850961783 5.0833310067896917417 -6.9952686384852365009 -15.589189007311734514 -1.1711611083994513116 -50.691993769147728699 -4.8065510100469497345 -25.287615343990143657;23.316464668171921204 -2.6088956283913602441 13.041101615754492116 41.728557110756092641 90.266578963239297195 94.493035331248250941 -191.05912521655361047 -28.238076284169057573 127.54673692012541153;-2.1771924781919054226 0.067726561580941146978 0.14338787220798443478 -1.339949216050258185 1.7163969686911912937 -2.6604507908781567238 8.1332666519249645631 4.924428410008625967 -6.5543165662320692633;-3.348678695354458501 -1.5680372794989216878 0.27307087376080829699 -1.3383775110607574188 -1.6316830295007656026 -1.1137232718215253069 -3.1728695971194045278 4.4088039309288369338 -0.49194132499217013699;-7.309504572505836073 -43.31342118992181156 -3.9101029285353905429 -41.935531636170310321 12.668771166114854765 11.314578743853489939 -26.646630741641800455 -19.436144754926317546 -36.04895816082451887;0.17075762835867189238 0.014027345096528512705 0.92026840024487210901 1.1629024371201595045 1.4537059957695026569 -0.33600277214988999441 13.404906309462404579 -1.556501509278013895 1.0079460234520201123;-1.5949357089908291485 -11.450522421659645289 -1.8261098750576072458 -60.774874307154910014 3.5961322639924921951 -44.549038349625298849 95.723761880580852335 -1.8415134910587422912 -55.003679961517839558;18.663397307125837443 31.24535662239003031 -74.377663591138812649 5.224894902417616116 -2.4909686293333694884 43.832853802707511193 12.402803960343991463 -0.080583794041493087001 -3.7744707899790359562;0.078510822640818267448 0.017599896031012505354 -0.42655199778095342911 -0.60171642832842986426 2.5608911774674925077 -0.95102968292959855212 -1.9698728179169531227 -1.535732350233014909 -2.613179188546156162;0.23548973072085691016 0.19388075590495346123 0.14491746671550229109 -1.2401949804008831624 1.10749843142199067 -0.39076456039187812408 -2.9546058416355829301 -1.1164266247292604639 -1.3996153086115672437;-0.0021811114934069432414 0.89001471636056028736 -0.49923401581239346125 -0.15043418392211763135 -0.59224986523620126722 1.4354796150072617333 -1.5173952036896125595 -0.51792999928986138691 -4.3506669188617292932;1.5489841199544107653 5.0780073751128966819 -1.5872474777123319889 0.75115843724637465506 -0.20050024121638218566 5.1492068471111629435 -37.76157113869709292 2.0918933715785645866 0.90277048068356768873;-7.2351321255080209838 -2.1274258477218332963 1.4545842409648657156 -14.119641303080230799 -9.5620849942754215789 -38.32161302522558799 44.185963714709288297 14.272752410898714714 -26.417920583525891232;-2.271445340655171119 5.6488521533890878601 1.0025482915596339861 -6.8334230337547658962 4.8338256451351915288 -3.2984129339671839354 -20.842669133544848847 14.930850795854235358 -5.7892375365939479082;-4.7203280842873436285 -9.4801736494313590953 -12.5383121134529123 -91.899681899191861589 119.49729723905733181 -8.8506169282838591528 17.417615709502236143 -9.270480473762559015 -80.150206669647431568;-2.5719540579845125983 -4.3822545378570838537 23.441163723925299678 22.448225342357130074 -45.10275635394135918 -34.394698210513851677 97.990939163145739599 22.508057477285255743 -15.765462977359492314;1.7966171747993613383 -0.53918908236103779696 12.588316036713390389 -2.5310434009716691328 8.1604819737426410597 -25.789368301320195087 117.29821756233035046 2.2913662361171791559 -0.62221732643226101978;-5.1845554095006445294 6.2578779560735222631 -14.037024227551505362 -15.221784276688309134 -12.15124779306130165 -23.13900137605473617 4.2401278882782253987 5.4630926287382406414 -12.731608082287982242;-4.7707826072334107437 1.6199816476366426521 -3.325710439626545778 -7.4045728952047635829 22.556680888497492532 -13.072652719424157297 140.00809231502253738 -14.845057180083005122 22.676762832061584163;-0.47514683781920086236 0.25841993000261515023 18.277720264118496374 4.3365484918040406725 -43.058181517998896481 -21.888717436559343099 -1.1961874190776082827 8.0423306880789873219 -42.933155452830639831;-0.14616201837677481046 -0.13430583680996491247 -0.58981810779848353743 -0.71234313233794721576 -0.94576172672030411892 0.40095990570557238364 -12.496784049940304229 1.7251821978929184898 -0.24967894825909500711;-0.24768523280850157642 0.15698129187492410042 0.51470036967696175534 -3.5907044804731915733 2.1884295523676278172 -1.6632000458679307986 -0.4796569588994863409 -0.1551399226053817304 -4.9294948989068645417;-2.7287453132180869986 -1.4544804591226099255 0.78968765102461080385 3.1593992730923847745 -10.27080607048321248 7.5282558208640262265 -18.919787185772346305 -1.1997044417960491813 -7.9324348973540814711;-0.020087316557315798571 -6.2878594589471665799 -0.15921673533184060867 0.10681151766899948941 -19.482753493295533076 0.69934990760267923271 49.178631799995962126 8.6011789732938730424 -24.467347038979184504;10.536820677021587755 -5.9592909099740429824 7.30325400524276791 1.6305850397821675113 5.6674242183504404125 -13.112738862153801023 10.989253391707725527 -9.6079139493042600151 5.3981239648009360366;-1.2545559504385883631 -3.9407187706378463687 1.7841191405416487736 -0.04438681516755454276 -0.97981273712928496078 -3.055180465761397457 23.726156440946237325 -1.7410736286568402331 -1.2352073951740332181;-0.257453927816034156 -0.12600631787855620658 -0.15152952823034240848 1.2682606267108031961 -0.90327763788350612373 0.40935227214098013349 2.9434569338747058609 1.2958013233750498294 1.3485015078932933719;-2.8665527530112719923 -1.3469220643383554847 19.330563091396506081 -2.8084686040403927798 -20.837720313089857171 -2.4974630678810574302 -36.584511795294567094 -3.8823807714410580871 -29.935667863248351495;0.10500910940206639732 -1.8106148357266489413 -0.40274154876443618578 1.7744865512378684702 -0.10964838999231654726 2.4627956007507569858 5.4312246325547528514 -1.4946522692455372905 7.6143918559162928617;-17.524868537409059144 11.473587900867251221 -11.036495448527585239 13.848070543445940572 -68.275216891499823646 -26.95760708264942096 109.01583773742814287 15.377994621498990213 -31.770041826665824658;19.813957303264988496 -9.3539902595288513254 -15.474285874612549563 128.6624990280520251 -23.000347605868732614 129.75052280517553527 -184.61765106751099097 33.880235359246285043 95.366806157373488873;0.078401684752462688643 0.67125884757461906638 -3.4743703111094768055 5.0123440342991605334 3.961959600100572132 1.7965254711798910314 -5.4130896718341316998 4.6148080101037374234 2.7399910773318492119;0.67343729995913803599 -5.8064196051826186817 -2.156750128397398214 8.9472790411652223241 -26.48537336098555528 0.15778432423606658652 26.979468755386175616 -1.4477456026390456145 21.398770566964834927;19.260810759927970537 -114.51009442605032973 151.49555349226625367 43.325807586911970759 -63.851746588941395544 -126.06888223803258597 -53.498381454766942511 34.911387025219156044 -84.961824825503029501;19.540824835262984749 127.21152586406716978 -48.698541836292228879 105.99899513680173868 -91.611070019413659793 109.50365795113788181 44.952205352582467413 -25.630905529833334811 142.13678596912572516;2.8687917746736992797 2.1017964103411048704 0.64796848979679955161 3.1316218297456179798 8.8276278554390223974 -3.3465549234700460168 49.548364566834813161 -1.4167441180605313544 8.2104268366796162582;3.793719655147063996 -7.403383512684560408 -0.50729720905347186477 -3.0100811191782965714 11.389088713257267571 -6.5393939743041897827 8.8224831378762136325 1.0427688002066073381 -13.409485951237973822;-0.62697453496196120515 2.9744746187688848593 2.6558382984735904309 6.7255629796099061224 -14.671284399044981939 0.32956892820937788713 -54.585823382721201824 8.388313461119468073 6.70872018318471941;15.966360617271179834 2.4409881451986668033 28.622718596349749021 13.210462588859694932 -19.192201244219699419 37.104751522946713749 -45.229959593844732524 -26.079161591334976578 34.723500085622788447;5.3534276287246793657 2.6119345039259984631 0.17796061719564765236 3.1590891186620031483 -1.5197378601592319569 1.4997186010928065247 9.4753137105400959683 -0.64083826946580935147 2.5090832835909147036;0.3209390106003625065 16.04671332887873092 0.9731338277845179574 53.331329418804251929 -2.8345584896813305065 48.805815360403215664 38.412861999628738374 -3.7889178898026494302 84.390424788465665529];

% Layer 2
b2 = 0.30259117335102253543;
LW2_1 = [-0.0010971721057184389853 0.0083962246462983558537 -0.0027307629311519908757 0.0047120975772234497542 0.0021490591706695900444 0.080023017553646214051 2.5403240847166892458 -0.00074869403897206054845 -0.0017733637883615511934 -0.1595408196098820619 2.5458116184369377066 -0.004811520537812731535 0.0010863185703986527521 -0.0072937864033696415272 0.0029400955774635255564 -0.0024996059667202401126 -0.0023702866186851839075 0.0014195436572453502648 -0.0030939630859683439103 -0.016508118056806648372 -0.0015877051983461973415 -3.2224771976829793552 0.0016592626149794943019 -0.0041771451524016114595 -0.00099316165197425670084 -0.010980007358198231454 -0.081321183662134241543 0.00092156500812220305471 0.13321547062925354066 0.018882273589591935803 0.00090447353143817594851 -0.082209264930844183628 -0.76256777106001749633 0.16070425316996186926 -0.044072375853990868044 0.0012062660007474501709 0.0071363243742063519823 0.0012545007649656428859 -0.0017921228123160056356 0.0040542203402466276199 -0.0023157050835605100074 -0.0043400258937529752334 0.0019445559102905661704 0.13490895461397242605 0.048727434125739772786 0.0061903952558800337536 0.0045627361625012663113 -0.0024619138003385233546 -0.058857286292253396809 -0.70263178253066527201 -0.0032593428520068593035 -0.021764108480870965334 -0.0019231326569150186158 -0.0014740033825958534248 0.020248678060316771532 -0.0038159206545389273875 0.00036217485798284687051 -0.0014429413334346081511 -0.0094053482098095074482 -0.18730162255769791657 -0.0047594464035936425231 0.0018832467739314864841 -3.2268167121976776279 -0.0022594723102877527394];

% Output 1
y1_step1.ymin = -1;
y1_step1.gain = 0.00175936863902286;
y1_step1.xoffset = 1506.14754098361;

% ===== SIMULATION ========

% Dimensions
Q = size(x1,2); % samples

% Input 1
xp1 = mapminmax_apply(x1,x1_step1);

% Layer 1
a1 = tansig_apply(repmat(b1,1,Q) + IW1_1*xp1);

% Layer 2
a2 = repmat(b2,1,Q) + LW2_1*a1;

% Output 1
y1 = mapminmax_reverse(a2,y1_step1);
y1=y1.*x1(SAL,:)./35;
end

% ===== MODULE FUNCTIONS ========

% Map Minimum and Maximum Input Processing Function
function y = mapminmax_apply(x,settings)
  y = bsxfun(@minus,x,settings.xoffset);
  y = bsxfun(@times,y,settings.gain);
  y = bsxfun(@plus,y,settings.ymin);
end

% Sigmoid Symmetric Transfer Function
function a = tansig_apply(n,~)
  a = 2 ./ (1 + exp(-2*n)) - 1;
end

% Map Minimum and Maximum Output Reverse-Processing Function
function x = mapminmax_reverse(y,settings)
  x = bsxfun(@minus,y,settings.ymin);
  x = bsxfun(@rdivide,x,settings.gain);
  x = bsxfun(@plus,x,settings.xoffset);
end
