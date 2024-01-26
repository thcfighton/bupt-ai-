CREATE TABLE `exam`  (
  `t_id` int NOT NULL,
  `p_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `time` date NOT NULL,
  PRIMARY KEY (`t_id`, `p_id`)
);

CREATE TABLE `include`  (
  `p_id` int NOT NULL,
  `q_id` int NOT NULL,
  PRIMARY KEY (`p_id`, `q_id`)
);

CREATE TABLE `knowledge`  (
  `k_id` int NOT NULL,
  `contents` varchar(255) NOT NULL,
  PRIMARY KEY (`k_id`)
);

CREATE TABLE `question`  (
  `q_id` int NOT NULL,
  `k_id` int NOT NULL,
  `content` varchar(255) NOT NULL,
  `point` int NULL,
  `choice` varchar(255) NULL,
  `answer` char(2) NOT NULL,
  PRIMARY KEY (`q_id`, `k_id`)
);

CREATE TABLE `student`  (
  `s_id` int NOT NULL,
  `password` int NOT NULL,
  `name` varchar(255) NULL,
  PRIMARY KEY (`s_id`)
);

CREATE TABLE `take`  (
  `p_id` int NOT NULL,
  `s_id` int NOT NULL,
  `t_id` int NOT NULL,
  `grade` int NOT NULL,
  PRIMARY KEY (`s_id`, `p_id`, `t_id`)
);

CREATE TABLE `teacher`  (
  `t_id` int NOT NULL,
  `password` varchar(25) NOT NULL,
  `name` varchar(20) NULL,
  PRIMARY KEY (`t_id`)
);

CREATE TABLE `test paper`  (
  `p_id` int NOT NULL,
  `paper_title` varchar(25) NOT NULL,
  `size` int NOT NULL,
  PRIMARY KEY (`p_id`)
);

ALTER TABLE `exam` ADD CONSTRAINT `fk_exam_teacher_1` FOREIGN KEY (`t_id`) REFERENCES `teacher` (`t_id`);
ALTER TABLE `exam` ADD CONSTRAINT `fk_exam_test paper_1` FOREIGN KEY (`p_id`) REFERENCES `test paper` (`p_id`);
ALTER TABLE `include` ADD CONSTRAINT `fk_include_question_1` FOREIGN KEY (`q_id`) REFERENCES `question` (`q_id`);
ALTER TABLE `include` ADD CONSTRAINT `fk_include_test paper_1` FOREIGN KEY (`p_id`) REFERENCES `test paper` (`p_id`);
ALTER TABLE `question` ADD CONSTRAINT `fk_question_knowledge_1` FOREIGN KEY (`k_id`) REFERENCES `knowledge` (`k_id`);
ALTER TABLE `take` ADD CONSTRAINT `fk_take_student_1` FOREIGN KEY (`s_id`) REFERENCES `student` (`s_id`);
ALTER TABLE `take` ADD CONSTRAINT `fk_take_exam_1` FOREIGN KEY (`p_id`) REFERENCES `exam` (`p_id`);
ALTER TABLE `take` ADD CONSTRAINT `fk_take_exam_2` FOREIGN KEY (`t_id`) REFERENCES `exam` (`t_id`);

