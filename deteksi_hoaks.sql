
-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 31 Agu 2025 pada 08.21
-- Versi server: 8.0.43
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `deteksi_hoaks`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `admin`
--

CREATE TABLE `admin` (
  `id` int NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'holis', 'admin12345');

-- --------------------------------------------------------

--
-- Struktur dari tabel `history`
--

CREATE TABLE `history` (
  `id` int NOT NULL,
  `text` text COLLATE utf8mb4_general_ci NOT NULL,
  `prediction` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `confidence` float NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `history`
--

INSERT INTO `history` (`id`, `text`, `prediction`, `confidence`, `timestamp`) VALUES
(2, 'Ganjar Pranowo Mengatakan “Saya akan menghapus utang negara dalam waktu 5 tahun”', 'FAKE', 78.7802, '2025-08-10 07:56:50'),
(3, 'Kapolri Jenderal Listyo Sigit Prabowo Lantik Sejumlah Kapolda Baru', 'REAL', 96.1431, '2025-08-10 08:33:50'),
(4, 'Lowongan Kerja Mengatasnamakan PT Bank Mandiri (Persero) Tbk', 'FAKE', 99.3897, '2025-08-10 16:41:26'),
(5, '\"Kominfo Ajak Masyarakat Perangi Hoaks dan Ujaran Kebencian\"', 'REAL', 93.8626, '2025-08-10 17:05:30'),
(6, 'Ganjar Pranowo Mengatakan “Saya akan menghapus utang negara dalam waktu 5 tahun', 'FAKE', 78.7802, '2025-08-10 17:22:07'),
(7, '\"Menteri BUMN Tunjuk Direktur Utama Baru untuk Pelindo', 'REAL', 96.9678, '2025-08-10 17:22:20'),
(8, 'Lowongan Kerja Bank Syariah Indonesia untuk Lulusan SMA/SMK Sederajat', 'FAKE', 70.188, '2025-08-17 14:40:13'),
(9, 'Jadwal Siaran Langsung Debut Megawati di Manisa BBSK', 'REAL', 95.7366, '2025-08-30 16:25:35'),
(10, 'Surat Panggilan Tes Calon Karyawan PT Erajaya Swasembada Tbk', 'FAKE', 99.0268, '2025-08-30 16:26:03'),
(11, 'Jadwal Siaran Langsung Debut Megawati di Manisa BBSK', 'REAL', 95.7366, '2025-08-30 16:26:24'),
(12, 'Kampus Universitas Hamzanwadi Melakukan Pungli pada Mahasiswa Karena Rektor Gagal dalam Pencalonan sebagai Gubernur', 'REAL', 90.9176, '2025-08-30 16:29:37'),
(13, 'Kampus Universitas Hamzanwadi Melakukan Pungli pada Mahasiswa Karena Rektor Gagal dalam Pencalonan sebagai Gubernur', 'REAL', 90.9176, '2025-08-30 16:29:46'),
(14, 'Kampus Universitas Hamzanwadi Melakukan Pungli pada Mahasiswa Karena Rektor Gagal dalam Pencalonan sebagai Gubernur', 'REAL', 90.9176, '2025-08-30 16:30:53'),
(15, 'Anies Baswedan Mengatakan Bahwa Dirinya Akan Menjadikan Indonesia sebagai Negara dengan Tingkat Korupsi Terendah di Dunia\"', 'FAKE', 99.3419, '2025-08-30 16:31:53'),
(16, 'Kampus Universitas Hamzanwadi Melakukan Pungli pada Mahasiswa Karena Rektor Gagal dalam Pencalonan sebagai Gubernur', 'REAL', 90.9176, '2025-08-30 16:32:02');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indeks untuk tabel `history`
--
ALTER TABLE `history`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT untuk tabel `history`
--
ALTER TABLE `history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
