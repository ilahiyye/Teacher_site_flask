-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Anamakine: 127.0.0.1
-- Üretim Zamanı: 19 Eki 2019, 20:31:17
-- Sunucu sürümü: 10.1.29-MariaDB
-- PHP Sürümü: 7.1.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Veritabanı: `telebe_platformasi`
--

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `articles`
--

CREATE TABLE `articles` (
  `id` int(11) NOT NULL,
  `title` text NOT NULL,
  `author` text NOT NULL,
  `content` text NOT NULL,
  `created_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Tablo döküm verisi `articles`
--

INSERT INTO `articles` (`id`, `title`, `author`, `content`, `created_date`) VALUES
(16, 'Yoxlama', 'Amar', '<p>I LIKE PYTHON</p>', '2019-10-10 14:26:37'),
(18, 'Python', 'ilahiye ', '<p>Bu bir yoxlamadir</p>', '2019-10-14 10:04:28');

-- --------------------------------------------------------

--
-- Tablo için tablo yapısı `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `FirstName` varchar(255) NOT NULL,
  `LastName` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `sector` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Tablo döküm verisi `users`
--

INSERT INTO `users` (`id`, `FirstName`, `LastName`, `name`, `sector`, `email`, `password`) VALUES
(1, 'ilahiyə', 'Musayeva', 'ilahiye', 'tk20', 'ilahiyye@gmail.com', '$5$rounds=535000$XE8mYjoXaKXpMga5$.l5xmAGyy.SEG8Dkxfg1K5fkMic6Ba1xBCERzIDpSc/'),
(2, 'Amar', 'Musayev', 'Amar', '7b', 'amarmusayev67@gmail.com', '$5$rounds=535000$w.1uFDa.dVIFNaA/$/9Mf8yYiqoWbUUB0zFHZ1YzSsLhgQjsq9IHYHbDNgq8'),
(3, 'Sevinc', 'Zeynalova', 'Sevinc', '873', 'seva_z_h_@mail.ru', '$5$rounds=535000$1ctdIqYynEBVn2L9$yv0IybqWm0fK26kwmr03WqxtuUEupzPsITSf62JRcW/');

--
-- Dökümü yapılmış tablolar için indeksler
--

--
-- Tablo için indeksler `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`id`);

--
-- Tablo için indeksler `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- Dökümü yapılmış tablolar için AUTO_INCREMENT değeri
--

--
-- Tablo için AUTO_INCREMENT değeri `articles`
--
ALTER TABLE `articles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- Tablo için AUTO_INCREMENT değeri `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
