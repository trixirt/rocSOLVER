%global upstreamname rocSOLVER
%global rocm_release 5.7
%global rocm_patch 1
%global rocm_version %{rocm_release}.%{rocm_patch}

%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/')

# No debug source produced
%global debug_package %{nil}

# $gpu will be evaluated in the loops below
%global _vpath_builddir %{_vendor}-%{_target_os}-build-${gpu}

# Tests are downloaded so this option is only good for local building
# Also need to
# export QA_RPATHS=0xff
%bcond_with test

# Fortran is only used in testing
%global build_fflags %{nil}

Name:           rocsolver
Version:        %{rocm_version}
Release:        1%{?dist}
Summary:        Next generation LAPACK implementation for ROCm platform
Url:            https://github.com/ROCmSoftwarePlatform/%{upstreamname}
License:        MIT

# Only x86_64 works right now:
ExclusiveArch:  x86_64

Source0:        %{url}/archive/refs/tags/rocm-%{rocm_version}.tar.gz#/%{upstreamname}-%{rocm_version}.tar.gz

BuildRequires:  cmake
BuildRequires:  compiler-rt
BuildRequires:  clang-devel
BuildRequires:  fmt-devel
BuildRequires:  lld
BuildRequires:  llvm-devel
BuildRequires:  ninja-build
BuildRequires:  rocblas-devel
BuildRequires:  rocm-cmake
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-hip-devel
BuildRequires:  rocm-runtime-devel
BuildRequires:  rocm-rpm-macros
BuildRequires:  rocm-rpm-macros-modules
BuildRequires:  rocprim-devel

%if %{with test}
BuildRequires:  blas-static
BuildRequires:  gcc-gfortran
BuildRequires:  gtest-devel
BuildRequires:  lapack-static
BuildRequires:  libomp-devel
BuildRequires:  rocsparse-devel
%endif

%description
rocSOLVER is a work-in-progress implementation of a subset
of LAPACK functionality on the ROCm platform.

%package devel
Summary: Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%prep
%autosetup -p1 -n %{upstreamname}-rocm-%{version}

%build
for gpu in %{rocm_gpu_list}
do
    module load rocm/$gpu
    %cmake %rocm_cmake_options \
	   -DCMAKE_CXX_FLAGS="-mcmodel=medium" \
%if %{with test}
           -DBUILD_CLIENTS_TESTS=ON
%endif

    %cmake_build
    module purge
done

%cmake_build

%install
for gpu in %{rocm_gpu_list}
do
    %cmake_install
done

%files
%license LICENSE.md
%exclude %{_docdir}/%{name}/LICENSE.md
%{_libdir}/lib%{name}.so.*
%{_libdir}/rocm/gfx*/lib/lib%{name}.so.*

%files devel
%dir %{_includedir}/%{name}
%dir %{_libdir}/cmake/%{name}
%dir %{_libdir}/rocm/gfx8/lib/cmake/%{name}
%dir %{_libdir}/rocm/gfx9/lib/cmake/%{name}
%dir %{_libdir}/rocm/gfx10/lib/cmake/%{name}
%dir %{_libdir}/rocm/gfx11/lib/cmake/%{name}

%doc README.md
%{_includedir}/%{name}/*.h
%{_libdir}/cmake/%{name}/*.cmake
%{_libdir}/lib%{name}.so
%{_libdir}/rocm/gfx*/lib/lib%{name}.so
%{_libdir}/rocm/gfx*/lib/cmake/%{name}/*.cmake

%if %{with test}
%files test
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/test
%dir %{_datadir}/%{name}/test/mat_20_60
%dir %{_datadir}/%{name}/test/mat_20_100
%dir %{_datadir}/%{name}/test/mat_20_140
%dir %{_datadir}/%{name}/test/mat_50_60
%dir %{_datadir}/%{name}/test/mat_50_100
%dir %{_datadir}/%{name}/test/mat_50_140
%dir %{_datadir}/%{name}/test/mat_100_300
%dir %{_datadir}/%{name}/test/mat_100_500
%dir %{_datadir}/%{name}/test/mat_100_700
%dir %{_datadir}/%{name}/test/mat_250_300
%dir %{_datadir}/%{name}/test/mat_250_500
%dir %{_datadir}/%{name}/test/mat_250_700

%{_datadir}/%{name}/test/mat_20_60/*
%{_datadir}/%{name}/test/mat_20_100/*
%{_datadir}/%{name}/test/mat_20_140/*
%{_datadir}/%{name}/test/mat_50_60/*
%{_datadir}/%{name}/test/mat_50_100/*
%{_datadir}/%{name}/test/mat_50_140/*
%{_datadir}/%{name}/test/mat_100_300/*
%{_datadir}/%{name}/test/mat_100_500/*
%{_datadir}/%{name}/test/mat_100_700/*
%{_datadir}/%{name}/test/mat_250_300/*
%{_datadir}/%{name}/test/mat_250_500/*
%{_datadir}/%{name}/test/mat_250_700/*
%{_bindir}/%{name}*
%{_libdir}/rocm/gfx*/bin/%{name}*
%endif

%changelog
* Thu Nov 2 2023 Tom Rix <trix@redhat.com>  - 5.7.1-1
- Initial package
