#!/usr/bin/env python3


 public static final Platform SPIKE32 =
      Platform.builder()
          .riscvBuilder()
          .can32Bit()
          .platform("spike")
          .simulationBinary("riscv32")
          .march("rv32imac")
          .build();

  public static final Platform SPIKE64 =
      Platform.builder()
          .riscvBuilder()
          .can64Bit()
          .platform("spike")
          .simulationBinary("riscv64")
          .march("rv64imac")
          .build();
  public static final Platform hifive =
      Platform.builder()
          .riscvBuilder()
          .can64Bit()
          .platform("hifive")
          .req("hifive1")
          .march("rv64imac")
          .build();

  public static final Platform SABRE =
      Platform.builder()
          .armBuilder()
          .platform("sabre")
          .imagePlatform("imx6")
          .req("sabre-family")
          .can32SMP()
          .can32Bit()
          .simulationBinary("sabre")
          .march("armv7a")
          .build();

  public static final Platform ROCKPRO64 =
      Platform.builder()
          .armBuilder()
          .platform("rockpro64")
          .req("rockpro64-family")
          .can64Bit()
          .march("armv7a")
          .build();

  public static final Platform IMX8MQ_EVK =
      Platform.builder()
          .armBuilder()
          .platform("imx8mq-evk")
          .req("imx8mq-family")
          .can64SMP()
          .can64Bit()
          .march("armv8a")
          .build();
  public static final Platform IMX8MM_EVK =
      Platform.builder()
          .armBuilder()
          .platform("imx8mm-evk")
          .req("imx8mm-family")
          .can64Bit()
          .can32Bit()
          .can64SMP()
          .march("armv8a")
          .build();
  public static final Platform KZM =
      Platform.builder()
          .armBuilder()
          .platform("kzm")
          .imagePlatform("imx31")
          .req("kzm")
          .simulationBinary("kzm11")
          .can32Bit()
          .march("armv6a")
          .disabled(true)
          .build();
  public static final Platform OMAP3 =
      Platform.builder()
          .armBuilder()
          .platform("omap3")
          .req("beagle")
          .can32Bit()
          .march("armv7a")
          .build();
  public static final Platform AM335X_BONEBLACK =
      Platform.builder()
          .armBuilder()
          .platform("am335x-boneblack")
          .imagePlatform("am335x")
          .req("bboneblack")
          .can32Bit()
          .march("armv8a")
          .build();
  public static final Platform ODROID_C2 =
      Platform.builder()
          .armBuilder()
          .platform("odroidc2")
          .req("odroidc2")
          .can64Bit()
          .march("armv8a")
          .build();
  public static final Platform ODROID_X =
      Platform.builder()
          .armBuilder()
          .platform("exynos4")
          .req("odroid")
          .can32Bit()
          .march("armv7a")
          .build();
  public static final Platform ODROID_XU =
      Platform.builder()
          .armBuilder()
          .platform("exynos5410")
          .req("odroid-xu")
          .imagePlatform("exynos5")
          .can32Bit()
          .aarch32hyp()
          .march("armv7a")
          .build();

  public static final Platform ARNDALE =
      Platform.builder()
          .armBuilder()
          .platform("exynos5250")
          .req("arndale")
          .imagePlatform("exynos5")
          .can32Bit()
          .march("armv7a")
          .build();

  public static final Platform ODROID_XU4 =
      Platform.builder()
          .armBuilder()
          .platform("exynos5422")
          .req("odroid-xu4-1")
          .imagePlatform("exynos5")
          .can32Bit()
          .aarch32hyp()
          .march("armv7a")
          .build();
  public static final Platform ZYNQ7000 =
      Platform.builder()
          .armBuilder()
          .platform("zynq7000")
          .req("zc706")
          .can32Bit()
          .simulationBinary("zc706")
          .march("armv7a")
          .build();
  public static final Platform ZYNQMP =
      Platform.builder()
          .armBuilder()
          .platform("zynqmp")
          .req("zcu102")
          .can64SMP()
          .can64Bit()
          .march("armv8a")
          .build();
  public static final Platform HIKEY =
      Platform.builder()
          .armBuilder()
          .platform("hikey")
          .req("hikey")
          .aarch64hyp()
          .can32Bit()
          .can64Bit()
          .march("armv8a")
          .build();
  public static final Platform TK1 =
      Platform.builder()
          .armBuilder()
          .platform("tk1")
          .req("jetson")
          .aarch32hyp()
          .can32Bit()
          .march("armv7a")
          .build();
  public static final Platform RPI3 =
      Platform.builder()
          .armBuilder()
          .platform("rpi3")
          .req("rpi3")
          .imagePlatform("bcm2837")
          .can32Bit()
          .march("armv8a")
          .build();
  public static final Platform TX1 =
      Platform.builder()
          .armBuilder()
          .platform("tx1")
          .req("jetson tx1 family")
          .can64Bit()
          .aarch64hyp()
          .can64SMP()
          .march("armv8a")
          .build();
  public static final Platform TX2 =
      Platform.builder()
          .armBuilder()
          .platform("tx2")
          .req("tx2_family")
          .can64Bit()
          .aarch64hyp()
          .can64SMP()
          .march("armv8a")
          .build();
  public static final Platform APQ8064 =
      Platform.builder()
          .armBuilder()
          .platform("apq8064")
          .req("inforce")
          .imagePlatform("inforce")
          .can32Bit()
          .march("armv7a")
          .build(); // Snapdragon board, has no bamboo tests
  public static final Platform WANDQ =
      Platform.builder().armBuilder().platform("wandq").imagePlatform("imx6").can32Bit().build();
  public static final Platform ALLWINNER20 =
      Platform.builder().armBuilder().platform("allwinner20").can32Bit().build();
  public static final Platform IMX7SABRE =
      Platform.builder()
          .armBuilder()
          .platform("imx7sabre")
          .req("imx7")
          .imagePlatform("imx7")
          .can32Bit()
          .build();

  /* generic x86 machines */
  public static final Platform PC99 =
      Platform.builder()
          .x86Builder()
          .platform("x86_64")
          .req("x64")
          .simulationBinary("x86")
          .march("nehalem")
          .build();

  /* specific named machines */
  public static final Machine HASWELL1 = new Machine(PC99, "haswell1");
  public static final Machine HASWELL2 = new Machine(PC99, "haswell2");
  public static final Machine HASWELL3 = new Machine(PC99, "haswell3");
  public static final Machine HASWELL4 = new Machine(PC99, "haswell4");
  public static final Machine SKYLAKE = new Machine(PC99, "skylake1");
  public static final Machine SANDY = new Machine(PC99, "sandy");
  public static final Machine TARDEC2 = new Machine(PC99, "tardec2");
